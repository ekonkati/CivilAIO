# CivilAIO Platform (PRD + Backend Scaffold)

This repository tracks the AI-native building design, estimation, and execution platform described in the provided PRD and contains an initial backend scaffold to begin implementation.

## Repository contents
- `MASTER PRD for Prompt to Project Completion.pdf`: original PRD.
- `read_prd.py`: PDF extractor (prefers PyPDF2, falls back to an internal decoder).
- `prd_text.txt`: latest extracted PRD text (still contains some garbled sections).
- `sync_myprd.py`: helper to pull `myprd.txt` from a GitHub raw URL or verify its presence.
- `IMPLEMENTATION_PLAN.md`: expanded delivery and milestone plan.
- `app/`: FastAPI backend scaffold with health and requirement capture endpoints.
- `tests/`: pytest coverage for the scaffold.
- `.env.example`: sample environment configuration for the backend.
- `requirements.txt`: dependencies for extraction and the backend scaffold.
- `Makefile`: helper commands for install, lint, test, and run.

## Backend scaffold
The scaffold aligns with Phase M1 of the implementation plan and now walks through the PRD journey from requirement capture to costing:
- `GET /api/health`: reports service status, environment, version, and declared modules mapped to PRD capabilities.
- `POST /api/briefs`: echoes a high-level project requirement (title, location, preferred codes, structure types, description).
- `POST /api/projects`: seeds a project from a requirement brief and auto-generates a layout, structural skeleton, estimation, and execution milestones using deterministic heuristics.
- `GET /api/projects/{id}`: retrieves the unified record (requirement → layout → structure → costing → execution).
- `POST /api/projects/{id}/layout`: regenerates the layout proposal from the stored requirement.
- `POST /api/projects/{id}/structure`: regenerates the structural understanding (columns, beams, slab/foundation, seismic/wind tags).
- `POST /api/projects/{id}/estimate`: refreshes SSR/SOR-based costing and execution plan.

### Quickstart
```bash
make install              # install dependencies
cp .env.example .env      # configure overrides as needed
make test                 # run pytest suite
make run                  # start FastAPI on http://localhost:8000
```

For a full happy-path demo:
```bash
curl -s -X POST http://localhost:8000/api/projects \
  -H "Content-Type: application/json" \
  -d '{"title":"G+2 in Hyderabad","location":"Hyderabad","usage":"residential","floors":3,"footprint_m2":120,"preferred_codes":["IS 456"],"structure_types":["RCC"],"regional_rate":"telangana-2024"}'
```
Then open `http://localhost:8000/docs` to rerun layout/structure/estimate actions.

## PRD reconciliation
`myprd.txt` is not present in this snapshot. To reconcile it with `prd_text.txt`:
```bash
python sync_myprd.py --url <raw_github_url>  # or place myprd.txt manually and rerun without --url
```
Document deltas in `docs/prd_recon.md` (per implementation plan) before expanding features beyond the scaffold.

## How to rerun PDF extraction
```bash
pip install -r requirements.txt  # if external installs are permitted
python read_prd.py
```
If PyPDF2 cannot be installed, the fallback parser will still refresh `prd_text.txt` with best-effort extraction.
