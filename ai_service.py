import json
import os
import re
from typing import Any

import httpx


INFERENCE_URL = "https://inference.do-ai.run/v1/chat/completions"
MODEL_NAME = os.getenv("DO_INFERENCE_MODEL", "anthropic-claude-4.6-sonnet")


def _extract_json(text: str) -> str:
    m = re.search(r"```(?:json)?\s*\n?([\s\S]*?)\n?\s*```", text, re.DOTALL)
    if m:
        return m.group(1).strip()
    m = re.search(r"(\{.*\}|\[.*\])", text, re.DOTALL)
    if m:
        return m.group(1).strip()
    return text.strip()


def _coerce_unstructured_payload(raw_text: str) -> dict[str, object]:
    compact = raw_text.strip()
    normalized = compact.replace("\n", ",")
    tags = [part.strip(" -•\t") for part in normalized.split(",") if part.strip(" -•\t")]
    if not tags:
        tags = ["guided plan", "saved output", "shareable insight"]
    headline = tags[0].title()
    items = []
    for index, tag in enumerate(tags[:3], start=1):
        items.append({
            "title": f"Stage {index}: {tag.title()}",
            "detail": f"Use {tag} to move the request toward a demo-ready outcome.",
            "score": min(96, 80 + index * 4),
        })
    highlights = [tag.title() for tag in tags[:3]]
    return {
        "note": "Model returned plain text instead of JSON",
        "raw": compact,
        "text": compact,
        "summary": compact or f"{headline} fallback is ready for review.",
        "tags": tags[:6],
        "items": items,
        "score": 88,
        "insights": [f"Lead with {headline} on the first screen.", "Keep one clear action visible throughout the flow."],
        "next_actions": ["Review the generated plan.", "Save the strongest output for the demo finale."],
        "highlights": highlights,
    }

def _normalize_inference_payload(payload: object) -> dict[str, object]:
    if not isinstance(payload, dict):
        return _coerce_unstructured_payload(str(payload))
    normalized = dict(payload)
    summary = str(normalized.get("summary") or normalized.get("note") or "AI-generated plan ready")
    raw_items = normalized.get("items")
    items: list[dict[str, object]] = []
    if isinstance(raw_items, list):
        for index, entry in enumerate(raw_items[:3], start=1):
            if isinstance(entry, dict):
                title = str(entry.get("title") or f"Stage {index}")
                detail = str(entry.get("detail") or entry.get("description") or title)
                score = float(entry.get("score") or min(96, 80 + index * 4))
            else:
                label = str(entry).strip() or f"Stage {index}"
                title = f"Stage {index}: {label.title()}"
                detail = f"Use {label} to move the request toward a demo-ready outcome."
                score = float(min(96, 80 + index * 4))
            items.append({"title": title, "detail": detail, "score": score})
    if not items:
        items = _coerce_unstructured_payload(summary).get("items", [])
    raw_insights = normalized.get("insights")
    if isinstance(raw_insights, list):
        insights = [str(entry) for entry in raw_insights if str(entry).strip()]
    elif isinstance(raw_insights, str) and raw_insights.strip():
        insights = [raw_insights.strip()]
    else:
        insights = []
    next_actions = normalized.get("next_actions")
    if isinstance(next_actions, list):
        next_actions = [str(entry) for entry in next_actions if str(entry).strip()]
    else:
        next_actions = []
    highlights = normalized.get("highlights")
    if isinstance(highlights, list):
        highlights = [str(entry) for entry in highlights if str(entry).strip()]
    else:
        highlights = []
    if not insights and not next_actions and not highlights:
        fallback = _coerce_unstructured_payload(summary)
        insights = fallback.get("insights", [])
        next_actions = fallback.get("next_actions", [])
        highlights = fallback.get("highlights", [])
    return {
        **normalized,
        "summary": summary,
        "items": items,
        "score": float(normalized.get("score") or 88),
        "insights": insights,
        "next_actions": next_actions,
        "highlights": highlights,
    }


async def _call_inference(messages, max_tokens: int = 512) -> dict[str, Any]:
    token = os.getenv("GRADIENT_MODEL_ACCESS_KEY") or os.getenv("DIGITALOCEAN_INFERENCE_KEY")
    if not token:
        return {"note": "AI temporarily unavailable: missing inference key."}

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "temperature": 0.4,
        "max_completion_tokens": max_tokens,
    }

    try:
        async with httpx.AsyncClient(timeout=90.0) as client:
            response = await client.post(INFERENCE_URL, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

        content = ""
        choices = data.get("choices", [])
        if choices:
            content = choices[0].get("message", {}).get("content", "")

        extracted = _extract_json(content)
        parsed = json.loads(extracted)
        if isinstance(parsed, dict):
            return parsed
        return {"data": parsed}
    except Exception as exc:
        return {"note": f"AI temporarily unavailable. Showing fallback output. ({str(exc)[:180]})"}


async def build_weekly_plan_with_ai(user_context: dict[str, Any]) -> dict[str, Any]:
    prompt = {
        "role": "user",
        "content": (
            "Create a 5-meal daily nutrition plan in strict JSON with keys: summary, items, score. "
            "items must be an array of meal objects each with day, slot, title, prep_minutes, calories, protein_g, carbs_g, fats_g, "
            "ingredients (array of strings), pantry_tags (array of strings). "
            "Keep output practical and nutritionally plausible. Context: "
            f"{json.dumps(user_context)}"
        ),
    }
    return await _call_inference([
        {"role": "system", "content": "You are a nutrition planning assistant that outputs strict JSON only."},
        prompt,
    ])


async def generate_insights_with_ai(selection: dict[str, Any], context: str) -> dict[str, Any]:
    return await _call_inference([
        {"role": "system", "content": "Return strict JSON with keys insights, next_actions, highlights for meal planning."},
        {
            "role": "user",
            "content": f"Selection: {json.dumps(selection)}\nContext: {context}",
        },
    ])
