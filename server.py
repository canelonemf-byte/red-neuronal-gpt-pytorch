"""Servidor API REST del AGs-Core v1.1.0 — con autenticación y cliente web.

Arranque previsto (cuando el paquete esté completo):
  uvicorn ags_core.server:app --host 0.0.0.0 --port 8000

Este fichero vive hoy en la raíz del repo `red-neuronal-gpt-pytorch` como
fragmento importado desde Drive. El paquete Python `ags_core` (orchestrator,
learner, registry, memory, model, planner, tools, chat) NO está en este
repositorio ni se ha encontrado en otros repos/backups del autor con la
API que este servidor exige (`Orchestrator(CFG)` + `learner._best_loss()`).

Autoría: Lázaro López Paz, El Prat de Llobregat, Barcelona, España,
con asistencia de inteligencia artificial. ORCID 0000-0001-8601-1963. MIT.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MISSING: list[str] = []

_CFG_PATH = ROOT / "config.yaml"
if not _CFG_PATH.is_file():
    MISSING.append("config.yaml (en Drive: https://drive.google.com/file/d/1FPCRlJ1WWt6q9J6ThfRXJvO-_2Gq9Ik9/view)")

# Módulos del paquete ags_core v1.1.0 que server.py importa o usa vía Orchestrator.
_REQUIRED_PACKAGE_MODULES = (
    "orchestrator.py  (clase Orchestrator(CFG) con .subagents/.memory/.plan/.handle/.registry/.learner)",
    "learner.py       (método _best_loss usado por /api/v1/status)",
    "registry.py / memory.py / model.py / planner.py / tools.py / chat.py (paquete ags_core)",
    "__init__.py      (paquete importable como ags_core)",
)
for label in _REQUIRED_PACKAGE_MODULES:
    # No inventamos los ficheros: solo comprobamos si existen junto a este server
    # o bajo ags_core/.
    name = label.split()[0]
    here = ROOT / name
    pkg = ROOT / "ags_core" / name
    if not here.is_file() and not pkg.is_file():
        MISSING.append(label)

if MISSING:
    msg = (
        "red-neuronal-gpt-pytorch: entrada incompleta. Falta código REAL no inventado:\n  - "
        + "\n  - ".join(MISSING)
        + "\n\nEncontrado y restaurado desde Drive/backups del autor:\n"
        "  - config.yaml\n"
        "  - data/projects.json (registry conscious_universe v1.1)\n"
        "  - web/index.html (cliente chat ya presente en el repo)\n\n"
        "NO se ha copiado el orchestrator de ags-core / ags-core-v3-5 / radar_app:"
        " su API (Path/config.json o LiteLLM) no coincide con Orchestrator(CFG)"
        " + learner._best_loss() que este server.py exige.\n"
        "Cuando existan los módulos originales del autor, colócalos en ags_core/"
        " y vuelve a ejecutar.\n"
    )
    print(msg, file=sys.stderr)
    raise SystemExit(2)

# --- a partir de aquí solo si el paquete está completo (código original) ---
import os
import yaml
from fastapi import FastAPI, Header, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import Optional

os.chdir(ROOT)
CFG = yaml.safe_load(open("config.yaml", encoding="utf-8"))
from ags_core.orchestrator import Orchestrator  # type: ignore  # noqa: E402

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

web_dir = ROOT / "web"
web_dir.mkdir(exist_ok=True)
app.mount("/app", StaticFiles(directory=str(web_dir), html=True), name="web")

@app.get("/")
def root():
    return {"service": "AGs-Core", "version": "1.1.0", "auth": bool(TOKEN),
            "web_client": "/app/", "docs": "/docs",
            "endpoints": ["/api/v1/query", "/api/v1/status", "/api/v1/projects"]}

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
