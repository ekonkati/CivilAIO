# CivilAIO PRD Extraction Status

This repository currently contains:
- `MASTER PRD for Prompt to Project Completion.pdf`: the original PDF provided by the user.
- `read_prd.py`: a PDF extractor that prefers PyPDF2 and falls back to a Unicode-aware stream decoder when dependencies are unavailable.
- `prd_text.txt`: the latest extracted text (with some remaining garbled sections) produced by `read_prd.py`.
- `requirements.txt`: documents the intended PyPDF2 dependency for full-featured extraction.
- `sync_myprd.py`: a helper to pull `myprd.txt` from a GitHub raw URL or verify it exists locally.

## Current understanding of the PRD
Based on `prd_text.txt`, the PRD outlines an AI-native platform that automates the lifecycle from initial concept capture through architectural layouts, structural analysis, drawings, estimation, and project delivery. It emphasizes:
- AI-driven requirement extraction, architectural layout generation, and code-compliant structural design (Kratos/FEniCSx via Docker).
- Automated drawings/documents, SSR-based estimation, and project/workflow management for architects, engineers, contractors, and owners.
- Modularity, explainability, interoperability with BIM/CAD/IFC, and region-specific code/SSR support.
- Deployments around FastAPI, modular front-ends (React/Streamlit/Next.js), PostgreSQL + S3 storage, and scalable workers; monetization via freemium, pay-per-design, subscription, and enterprise tiers.

## Action needed: `myprd.txt`
The user referenced an uploaded `myprd.txt`, but it is not present in this repository snapshot. To reconcile requirements accurately, either:

1. Download via raw URL:
   ```bash
   python sync_myprd.py --url <raw_github_url>
   ```
2. Or copy `myprd.txt` into the repo root and verify:
   ```bash
   python sync_myprd.py
   ```

Once `myprd.txt` is available, compare it against `prd_text.txt` to confirm the extracted PDF content matches the authoritative requirements and unblock implementation.

## How to rerun extraction
```bash
pip install -r requirements.txt  # only if external installs are allowed
python read_prd.py
```
If PyPDF2 cannot be installed in the environment, the script will fall back to its built-in parser and still update `prd_text.txt` with the best-effort extraction.
