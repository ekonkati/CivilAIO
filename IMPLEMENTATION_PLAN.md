# CivilAIO Implementation Plan (Expanded)

This revision elaborates the delivery strategy so stakeholders can see the full scope, dependencies, and readiness to commit code changes. It still assumes `myprd.txt` will be synced (see `sync_myprd.py`) and reconciled against `prd_text.txt` before coding.

## 1) Source of Truth Reconciliation
1. Run `python sync_myprd.py --url <raw_url>` (or place `myprd.txt` manually) so both PRD sources are present in the repo.
2. Diff `myprd.txt` vs `prd_text.txt` and record deltas in `docs/prd_recon.md` (to be created) covering feature scope, constraints (Kratos via Docker, GPU needs, SSR locality), and billing tiers.
3. Update user stories/acceptance criteria after reconciliation, and lock a “PRD baseline” tag before engineering starts.

## 2) Platform Architecture & Foundations
1. Services: FastAPI (API/auth/rbac), worker queue (Celery/RQ with Redis), PostgreSQL + S3-compatible object store, and a Next.js/React (or Streamlit) front-end shell with SSR.
2. Shared contracts: 
   - **Domain models:** users, organizations, projects, sites, requirements, layouts, structural models, load cases, analysis results, drawings, BOQ items, schedules, QA/QC forms, documents.
   - **Artifact schemas:** Kratos input/output JSON, drawing vectors (DXF/SVG/IFC), report PDFs, estimation snapshots, and audit logs.
3. Infrastructure: Docker Compose for local, GitHub Actions CI for lint/test/type-check, and Makefile commands for dev workflow; secret management via `.env` templates.
4. Observability: structured logging, request/worker tracing, and feature flags for staged rollouts.

## 3) Requirement Capture & Layout Engine
1. UX: dual mode (chat + guided forms) to capture plot size, setbacks, floors, parking, roof use, soil/region, HVAC/electrical/resilience asks, and references (PDF/sketch/image uploads).
2. Layout generation: column grids, bay spacing, cores, circulation, parking, and furniture massing; export DXF/SVG; maintain revision history and AI-proposed alternates.
3. Intake adapters: vectorize sketches/PDFs; ingest CAD/IFC to seed geometry; normalize to a common layout schema for downstream structural generation.

## 4) Structural Modeling & Analysis
1. Auto-framing from layout to beams/columns/slabs/walls/footings/openings; recognize retaining/RE walls, tanks, and pile caps.
2. Load engine: gravity/live/roof/snow/wind/seismic generation from location/terrain; combinations per IS/ACI/AISC/Eurocode with code-specific envelopes.
3. Solver integration: translate geometry + loads into Kratos JSON; orchestrate Docker runs; capture reactions, envelopes, and member forces; support batch runs for alternates.
4. Design checks: RCC (IS 456/875/1893, ACI 318, Eurocode 2/8) and steel (IS 800/1893, AISC 360, Eurocode 3/8) including section selection, reinforcement detailing, serviceability, and deflection/drift limits.
5. Outputs: optimized member sizes, rebar schedules, and clause-referenced calculation sheets; cache runs for auditability.

## 5) Drawing & Documentation Engine
1. Auto-generate framing plans, GFCs, beam/column/footing details, connection drawings, rebar detailing, bar bending schedules, and hand-calculation-style reports.
2. Export pipeline: PDF/DXF/SVG/IFC with consistent layering, title blocks, scales, legends, and cross-references to calculations; maintain provenance hashes linking drawings to solver versions and inputs.
3. Review/markup workflow: allow comments, change requests, and revision clouds; versioned storage in S3 with signed URLs.

## 6) Estimation & BOQ
1. Quantity take-off tied to the model/drawings; maintain material libraries and assemblies; persist BOQ revisions with diff views.
2. Rate application: SSR/DSR/regional libraries + vendor overrides; scenario analysis (budget/premium/optimized) and sensitivity outputs.
3. Deliverables: item-wise abstracts, material consumption, manpower/equipment loading, cash-flow curves, and procurement-ready CSV/Excel exports.

## 7) Project Planning & Execution
1. Auto-WBS + Gantt from approved design/BOQ; track dependencies and critical path; provide progress dashboards (daily/weekly).
2. Site workflows: QA/QC checklists, measurement books, RA bills, approvals, NCRs/RFIs, document control, site photos, and correspondence drafting with AI assists.
3. Modularity: enable design-only, estimation-only, and PM-only modes with independent billing hooks and tenant scoping.

## 8) Interoperability & Template System
1. Imports: DXF, IFC, PDF/image/sketch vectorization, and STAAD (for migration); Exports: PDF/DXF/SVG/IFC/GLB and machine-readable JSON for re-use.
2. Template engine: parameterized templates per structure type (RCC/steel/PEB/retaining/RE walls/landfills/water tanks/etc.) covering loads, geometry, detailing, costing, and report styles; attach metadata to map templates to subscription tiers.
3. Continuous tuning: feedback loops from completed projects to improve AI suggestions and template defaults.

## 9) Commercial Model, Compliance & Safety
1. Billing: freemium requirement capture, pay-per-layout, pay-per-structural design, pay-per-detail sheet, pay-per-BOQ, and PM subscription; record usage events for invoicing.
2. Compliance: enforce Kratos via Docker; GPU/cloud for large models; local-only storage for regional SSR data; configurable paid inference for heavy AI steps.
3. Governance: audit logs for every transformation, clause references, override tracking, reproducible seeds for AI outputs, and PII/data residency controls.

## 10) Delivery Milestones (Engineering-Ready)
- **M1: Reconciliation & Scaffolding** — finalize PRD baseline; create FastAPI/Next.js/worker skeletons; Docker Compose; CI (lint/test/type-check); .env templates. _(Status: FastAPI scaffold extended with project seeding, layout/structure/estimation heuristics, and execution milestones; awaiting `myprd.txt` to complete reconciliation.)_
- **M2: Requirement & Layout MVP** — chat/forms intake, file uploads, vectorization spike, layout generator with revisions, template ingestion, persistence.
- **M3: Structural MVP** — auto-framing, load engine, Kratos Docker integration, RCC/steel checks (core clauses), caching, basic report stubs.
- **M4: Drawings** — plan/detail generation, export pipeline, provenance hashing, review/markup UI.
- **M5: Estimation** — QTO engine, rate libraries, BOQ revisions, scenario analysis, Excel/CSV exports.
- **M6: PM & Billing** — WBS/Gantt, dashboards, QA/QC/RA bill workflows, usage metering, subscription/pay-per-use plumbing.
- **M7: Hardening** — performance, GPU/cloud paths, security reviews, backups, monitoring, and template/AI tuning.

## 11) Work Packages & Ownership Clarity
- **Backend:** API contracts, domain models, queues, Kratos orchestration, estimation math, billing, audit.
- **Frontend:** Intake UI, drawing/plan viewers, review/markup, dashboards, billing UX.
- **Infra:** CI/CD, Docker images (app + Kratos), observability, secrets, backups.
- **Data/AI:** Prompt engineering, template curation, vectorization pipeline, model evaluation, feedback loops.

## 12) Validation & Next Steps
1. After `myprd.txt` reconciliation, publish user stories and acceptance tests per module.
2. Create a living RACI for each milestone and set up sprint cadences with demo checkpoints.
3. Begin M1 immediately and track risks (solver performance, GPU access, SSR data availability) with mitigation owners.
