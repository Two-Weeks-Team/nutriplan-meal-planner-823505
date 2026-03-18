from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

from models import init_db
from routes import router


app = FastAPI(title="Nutriplan Meal Planner API", version="1.0.0")


@app.on_event("startup")
def on_startup():
    init_db()



@app.middleware("http")
async def normalize_api_prefix(request: Request, call_next):
    if request.scope.get("path", "").startswith("/api/"):
        request.scope["path"] = request.scope["path"][4:] or "/"
    return await call_next(request)

app.include_router(router)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
def root():
    return """
<!DOCTYPE html>
<html>
<head>
  <meta charset='utf-8' />
  <meta name='viewport' content='width=device-width, initial-scale=1' />
  <title>Nutriplan Meal Planner API</title>
  <style>
    body { background:#0b1020; color:#e8ecff; font-family:Inter,system-ui,sans-serif; margin:0; }
    .wrap { max-width:980px; margin:40px auto; padding:24px; }
    .card { background:#121a32; border:1px solid #243056; border-radius:14px; padding:18px; margin-bottom:16px; }
    h1 { margin:0 0 8px; color:#9ad1ff; }
    a { color:#8ef0a8; }
    code { color:#ffd27d; }
    li { margin:6px 0; }
  </style>
</head>
<body>
  <div class='wrap'>
    <div class='card'>
      <h1>Nutriplan Meal Planner</h1>
      <p>AI meal planning that converts user goals into a complete, editable meal spread and grouped grocery output.</p>
      <p><a href='/docs'>OpenAPI Docs</a> · <a href='/redoc'>ReDoc</a></p>
    </div>
    <div class='card'>
      <h3>API Endpoints</h3>
      <ul>
        <li><code>GET /health</code></li>
        <li><code>GET /starter-profiles</code> and <code>GET /api/starter-profiles</code></li>
        <li><code>POST /macro-targets</code> and <code>POST /api/macro-targets</code></li>
        <li><code>POST /plan</code> and <code>POST /api/plan</code> (frontend contract)</li>
        <li><code>POST /insights</code> and <code>POST /api/insights</code> (frontend contract)</li>
        <li><code>GET /saved-plans</code> and <code>GET /api/saved-plans</code></li>
      </ul>
    </div>
    <div class='card'>
      <h3>Tech Stack</h3>
      <p>FastAPI 0.115.0 · SQLAlchemy 2.0.35 (sync) · Pydantic 2.9.0 · httpx 0.27.0 · PostgreSQL-ready with psycopg 3.2.3 · DigitalOcean Serverless Inference (anthropic-claude-4.6-sonnet)</p>
    </div>
  </div>
</body>
</html>
"""
