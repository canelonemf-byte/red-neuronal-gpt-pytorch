# red-neuronal-gpt-pytorch

Construcción de una red neuronal GPT en PyTorch (base documental de AGsGPT / AGs-Core v1.1).

## Autoría

- **Autor:** Lázaro López Paz, El Prat de Llobregat, Barcelona, España
- **ORCID:** [0000-0001-8601-1963](https://orcid.org/0000-0001-8601-1963)
- Elaborado con asistencia de inteligencia artificial
- Sin afiliaciones institucionales

## Estado verificado (2026-11-04, Europe/Madrid)

**No es ejecutable de extremo a extremo todavía.** Se ha verificado por búsqueda en:

- este repositorio y su historial git
- `ags-core`, `ags-core-v3-5`, `omniscience*`, backups locales y Google Drive del autor

### Restaurado (ficheros reales del autor)

| Fichero | Origen |
|---|---|
| `config.yaml` | Google Drive id `1FPCRlJ1WWt6q9J6ThfRXJvO-_2Gq9Ik9` |
| `data/projects.json` | Google Drive (registry conscious_universe: zero_a, neuroglyq, …) |
| `web/index.html` | copia del `index.html` ya presente en el repo (cliente chat) |

### Falta (no inventado)

El paquete Python `ags_core` v1.1.0 que `server.py` importa:

- `orchestrator.py` con API `Orchestrator(CFG)` y atributos `.subagents`, `.memory`, `.plan`, `.handle`, `.registry`, `.learner`
- `learner.py` con `_best_loss()` (usado por `/api/v1/status`)
- resto del paquete (`registry`, `memory`, `model`, `planner`, `tools`, `chat`, `__init__`)

En Drive/repos solo aparecen orquestadores **incompatibles** (p. ej. `radar_app` con `config.json`/`Path`, o AGs-Core v3.x con LiteLLM). **No se han copiado** para no fingir un runtime.

`python server.py` sale con código 2 y un mensaje claro listando lo que falta.

## Contenido

```
config.yaml
data/projects.json
docs/
index.html
web/index.html
LICENSE
NOTICE.md
README.md
REFERENCIAS.md
requirements.txt
server.py
```

## Instalación / uso

```bash
pip install -r requirements.txt
python server.py   # hoy: exit 2 con diagnóstico; no inventa el paquete
```

Cuando existan los módulos originales del autor, colócalos bajo `ags_core/` y el mismo `server.py` podrá arrancar sin reescritura inventada.

## Licencias y terceros

- Código de este repo: MIT (`LICENSE`), autor Lázaro López Paz.
- Referencias didácticas MIT (no se incluye su código aquí): minGPT / nanoGPT (A. Karpathy) — ver `NOTICE.md`.
- No se ha incorporado código con copyright restrictivo de terceros.
