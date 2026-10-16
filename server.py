"""Servidor API REST del AGs-Core v1.1.0 — con autenticación y cliente web.
Arranque:  uvicorn ags_core.server:app --host 0.0.0.0 --port 8000
Consulta:  POST http://<IP>:8000/api/v1/query  (header X-API-Key si hay token)
Chat web:  http://<IP>:8000/app/"""
import os, yaml
from pathlib import Path
from fastapi import FastAPI, Header, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import Optional

os.chdir(Path(__file__).resolve().parents[1])
ROOT = Path(__file__).resolve().parents[1]
CFG = yaml.safe_load(open("config.yaml", encoding="utf-8"))
from .orchestrator import Orchestrator

AGS = Orchestrator(CFG)
TOKEN = str(CFG.get("api", {}).get("token", ""))

def require_key(x_api_key: str = Header(default="")):
    """Autenticación: header 'X-API-Key'. Token vacío en config = modo desarrollo."""
    if TOKEN and x_api_key != TOKEN:
        raise HTTPException(status_code=401,
                            detail="No autorizado: header X-API-Key ausente o inválido")

app = FastAPI(title="AGs-Core API", version="1.1.0",
              description="Agente General de conscious_universe")

class Query(BaseModel):
    query: str = Field(..., min_length=1)
    project: Optional[str] = None
    plan: bool = False
    session: Optional[str] = None

class QueryResponse(BaseModel):
    response: str
    project: str
    mode: str
    experiences: int

# ── Cliente web (chat en navegador) ──
web_dir = ROOT / "web"
web_dir.mkdir(exist_ok=True)
app.mount("/app", StaticFiles(directory=str(web_dir), html=True), name="web")

@app.get("/")
def root():
    return {"service": "AGs-Core", "version": "1.1.0", "auth": bool(TOKEN),
            "web_client": "/app/", "docs": "/docs",
            "endpoints": ["/api/v1/query", "/api/v1/status", "/api/v1/projects"]}

# ── API protegida ──
@app.post("/api/v1/query", response_model=QueryResponse, dependencies=[Depends(require_key)])
def query(q: Query):
    pid = q.project
    if pid and pid not in AGS.subagents:
        return QueryResponse(response=f"Proyecto desconocido: {pid}. Válidos: {list(AGS.subagents)}",
                             project=pid, mode="error", experiences=AGS.memory.count())
    if q.plan:
        return QueryResponse(response=AGS.plan(q.query), project="plan",
                             mode="plan", experiences=AGS.memory.count())
    if pid:
        resp = AGS.subagents[pid].run(q.query)
        return QueryResponse(response=resp, project=pid, mode="agent",
                             experiences=AGS.memory.count())
    proj = AGS.registry.route(q.query)
    resp = AGS.handle(q.query)
    mode = "tool" if (proj and proj.tools) else ("nn" if "[AGs-NN" in resp else "heuristic")
    return QueryResponse(response=resp, project=proj.id if proj else "general",
                         mode=mode, experiences=AGS.memory.count())

@app.get("/api/v1/status", dependencies=[Depends(require_key)])
def status():
    return {"ecosystem": "conscious_universe",
            "projects": {p.id: p.status for p in AGS.registry.projects.values()},
            "experiences": AGS.memory.count(),
            "nn_best_loss": AGS.learner._best_loss(),
            "nn_active": AGS.learner._best_loss() <= float(CFG["model"]["nn_max_loss"])}

@app.get("/api/v1/projects", dependencies=[Depends(require_key)])
def projects():
    return [{"id": p.id, "domain": p.domain, "status": p.status,
             "tools": list(p.tools)} for p in AGS.registry.projects.values()]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
