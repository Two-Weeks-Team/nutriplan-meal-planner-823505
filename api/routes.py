import json
from datetime import datetime
from typing import Any, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ai_service import build_weekly_plan_with_ai, generate_insights_with_ai
from models import NPMeal, NPPlan, NPProfile, get_db


router = APIRouter()


class PlanRequest(BaseModel):
    query: str
    preferences: str


class InsightsRequest(BaseModel):
    selection: str
    context: str


class MacroInput(BaseModel):
    weight_kg: float
    activity_level: str
    goal: str
    dietary_style: Optional[str] = "balanced"
    restrictions: list[str] = Field(default_factory=list)


def _macro_targets(weight_kg: float, activity_level: str, goal: str) -> dict[str, Any]:
    activity_factor = {"light": 30, "moderate": 33, "high": 36}.get(activity_level, 32)
    calories = int(weight_kg * activity_factor)
    if goal == "fat_loss":
        calories -= 350
        protein_per_kg = 2.0
    elif goal == "muscle_gain":
        calories += 300
        protein_per_kg = 2.2
    else:
        protein_per_kg = 1.8

    protein_g = int(weight_kg * protein_per_kg)
    fats_g = int((calories * 0.28) / 9)
    carbs_g = int((calories - (protein_g * 4 + fats_g * 9)) / 4)
    explainer = (
        f"Calories start from weight ({weight_kg}kg) × activity factor ({activity_factor}). "
        f"Goal adjustment applied for {goal}. Protein set to {protein_per_kg} g/kg, fats at ~28% calories, carbs fill remainder."
    )
    return {
        "calories": max(calories, 1200),
        "protein_g": max(protein_g, 60),
        "carbs_g": max(carbs_g, 80),
        "fats_g": max(fats_g, 30),
        "explainer": explainer,
    }


def _fallback_items(days: int, targets: dict[str, Any]) -> list[dict[str, Any]]:
    slots = ["breakfast", "mid_morning_snack", "lunch", "dinner", "evening_snack"]
    catalog = {
        "breakfast": ("Greek Yogurt Berry Oats", ["oats", "greek yogurt", "berries", "chia"], 420, 32, 45, 12),
        "mid_morning_snack": ("Apple + Peanut Butter", ["apple", "peanut butter"], 240, 8, 26, 12),
        "lunch": ("Chicken Quinoa Bowl", ["chicken breast", "quinoa", "spinach", "olive oil"], 560, 46, 48, 18),
        "dinner": ("Salmon Rice Plate", ["salmon", "rice", "broccoli", "lemon"], 620, 44, 52, 22),
        "evening_snack": ("Cottage Cheese Nuts", ["cottage cheese", "almonds", "cinnamon"], 260, 22, 10, 14),
    }
    items = []
    for d in range(1, days + 1):
        for s in slots:
            t, ing, c, p, cb, f = catalog[s]
            items.append(
                {
                    "day": d,
                    "slot": s,
                    "title": t,
                    "prep_minutes": 10 if "snack" in s else 20,
                    "calories": c,
                    "protein_g": p,
                    "carbs_g": cb,
                    "fats_g": f,
                    "ingredients": ing,
                    "pantry_tags": ["salt", "pepper"] if s in ["lunch", "dinner"] else ["cinnamon"],
                }
            )
    return items


def _grocery_from_items(items: list[dict[str, Any]]) -> dict[str, list[str]]:
    groups = {"produce": [], "protein": [], "grains": [], "pantry": [], "extras": []}
    for it in items:
        for ing in it.get("ingredients", []):
            i = ing.lower()
            if i in ["spinach", "berries", "apple", "broccoli", "lemon"]:
                groups["produce"].append(ing)
            elif i in ["chicken breast", "salmon", "greek yogurt", "cottage cheese", "tofu", "eggs"]:
                groups["protein"].append(ing)
            elif i in ["oats", "rice", "quinoa"]:
                groups["grains"].append(ing)
            elif i in ["olive oil", "salt", "pepper", "cinnamon", "chia"]:
                groups["pantry"].append(ing)
            else:
                groups["extras"].append(ing)
    for k, v in groups.items():
        groups[k] = sorted(list(set(v)))
    return groups


@router.get("/starter-profiles")
@router.get("/starter-profiles")
def starter_profiles(db: Session = Depends(get_db)):
    rows = db.query(NPProfile).order_by(NPProfile.id.asc()).all()
    return [
        {
            "id": r.id,
            "name": r.name,
            "weight_kg": r.weight_kg,
            "activity_level": r.activity_level,
            "goal": r.goal,
            "dietary_style": r.dietary_style,
            "restrictions": json.loads(r.restrictions_json or "[]"),
        }
        for r in rows
    ]


@router.post("/macro-targets")
@router.post("/macro-targets")
def macro_targets(payload: MacroInput):
    return _macro_targets(payload.weight_kg, payload.activity_level, payload.goal)


@router.post("/plan")
@router.post("/plan")
async def create_plan(payload: PlanRequest, db: Session = Depends(get_db)):
    days = 3
    q = payload.query.lower()
    if "7" in q or "week" in q:
        days = 7

    inferred_weight = 68.0
    for token in payload.query.replace(",", " ").split():
        try:
            val = float(token)
            if 35 <= val <= 180:
                inferred_weight = val
                break
        except Exception:
            pass

    goal = "maintenance"
    if "loss" in q or "cut" in q:
        goal = "fat_loss"
    elif "gain" in q or "bulk" in q or "muscle" in q:
        goal = "muscle_gain"

    targets = _macro_targets(inferred_weight, "moderate", goal)

    ai = await build_weekly_plan_with_ai(
        {
            "query": payload.query,
            "preferences": payload.preferences,
            "days": days,
            "targets": targets,
        }
    )

    summary = ai.get("summary") if isinstance(ai, dict) else None
    items = ai.get("items") if isinstance(ai, dict) else None
    score = ai.get("score") if isinstance(ai, dict) else None

    if not isinstance(summary, str):
        summary = f"Generated a {days}-day plan with five meals per day aligned to {goal} targets."
    if not isinstance(items, list) or len(items) == 0:
        items = _fallback_items(days, targets)
    if not isinstance(score, (int, float)):
        score = 88.0

    grocery = _grocery_from_items(items)

    plan = NPPlan(
        name=f"Plan {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}",
        days=days,
        summary=summary,
        score=float(score),
        target_calories=targets["calories"],
        target_protein_g=targets["protein_g"],
        target_carbs_g=targets["carbs_g"],
        target_fats_g=targets["fats_g"],
        explainer=targets["explainer"],
        grocery_json=json.dumps(grocery),
        is_template=False,
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)

    for m in items:
        meal = NPMeal(
            plan_id=plan.id,
            day_index=int(m.get("day", 1)),
            slot=str(m.get("slot", "meal")),
            title=str(m.get("title", "Meal")),
            prep_minutes=int(m.get("prep_minutes", 15)),
            calories=int(m.get("calories", 400)),
            protein_g=int(m.get("protein_g", 20)),
            carbs_g=int(m.get("carbs_g", 40)),
            fats_g=int(m.get("fats_g", 12)),
            ingredients_json=json.dumps(m.get("ingredients", [])),
            pantry_tags_json=json.dumps(m.get("pantry_tags", [])),
        )
        db.add(meal)
    db.commit()

    return {"summary": summary, "items": items, "score": float(score)}


@router.post("/insights")
@router.post("/insights")
async def plan_insights(payload: InsightsRequest, db: Session = Depends(get_db)):
    ai = await generate_insights_with_ai({"selection": payload.selection}, payload.context)
    insights = ai.get("insights") if isinstance(ai, dict) else None
    next_actions = ai.get("next_actions") if isinstance(ai, dict) else None
    highlights = ai.get("highlights") if isinstance(ai, dict) else None

    if not isinstance(insights, list):
        insights = [
            "Lunch protein is a leverage point for satiety.",
            "Evening snack can be lighter to tighten calorie adherence.",
            "Current spread has strong ingredient overlap for easier shopping.",
        ]
    if not isinstance(next_actions, list):
        next_actions = [
            "Swap one lunch to a higher-protein bowl.",
            "Mark pantry staples you already own.",
            "Save this plan as a reusable weekly template.",
        ]
    if not isinstance(highlights, list):
        highlights = ["Macro balance is within target range.", "Grocery list is already grouped by aisle."]

    return {"insights": insights, "next_actions": next_actions, "highlights": highlights}


@router.get("/saved-plans")
@router.get("/saved-plans")
def saved_plans(db: Session = Depends(get_db)):
    plans = db.query(NPPlan).order_by(NPPlan.updated_at.desc()).limit(30).all()
    out = []
    for p in plans:
        out.append(
            {
                "id": p.id,
                "name": p.name,
                "days": p.days,
                "summary": p.summary,
                "score": p.score,
                "is_template": p.is_template,
                "updated_at": p.updated_at.isoformat() if p.updated_at else None,
            }
        )
    return out
