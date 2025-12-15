from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.config import get_settings
from app.models.core import HealthStatus, ModuleDescriptor, RequirementBrief
from app.models.project import LayoutPlan, Project, ProjectRequest, StructuralSkeleton
from app.services.pipeline import derive_structure, estimate_cost, execution_plan, propose_layout, seed_project

router = APIRouter()

MODULES = [
    ModuleDescriptor(
        key="requirement_engine",
        name="AI Requirement Engine",
        summary="Conversational capture of building briefs and constraints",
        billing_model="freemium + per-project",
        maturity="m1",
    ),
    ModuleDescriptor(
        key="layout_generator",
        name="Layout Generator",
        summary="Template- and AI-based architectural layouts with export",
        billing_model="per-layout",
        maturity="m2",
    ),
    ModuleDescriptor(
        key="structural_engine",
        name="Structural Analysis & Design",
        summary="Kratos-backed solver orchestration with IS/ACI/AISC checks",
        billing_model="per-structure",
        maturity="m3",
    ),
    ModuleDescriptor(
        key="drawings",
        name="Drawings & Detailing",
        summary="Auto-generated plans, rebar, and shop drawings with provenance",
        billing_model="per-sheet",
        maturity="m4",
    ),
    ModuleDescriptor(
        key="estimation",
        name="Estimation & BOQ",
        summary="SSR/SOR-based costing with scenarios and exports",
        billing_model="per-project",
        maturity="m5",
    ),
    ModuleDescriptor(
        key="execution",
        name="Project Execution",
        summary="WBS, Gantt, QA/QC, safety, and site reporting workflows",
        billing_model="subscription",
        maturity="m6",
    ),
]

PROJECTS: dict[str, Project] = {}


@router.get("/health", response_model=HealthStatus, tags=["ops"])
async def healthcheck() -> HealthStatus:
    settings = get_settings()
    return HealthStatus(
        status="ok",
        environment=settings.environment,
        version=settings.version,
        modules=MODULES,
    )


@router.post("/briefs", response_model=RequirementBrief, tags=["briefs"], status_code=201)
async def capture_brief(brief: RequirementBrief) -> RequirementBrief:
    """Return the captured brief; persistence will be added once storage is wired."""

    return brief


@router.post("/projects", response_model=Project, tags=["projects"], status_code=201)
async def create_project(request: ProjectRequest) -> Project:
    project = seed_project(request)
    PROJECTS[project.id] = project
    return project


@router.get("/projects/{project_id}", response_model=Project, tags=["projects"])
async def get_project(project_id: str) -> Project:
    project = PROJECTS.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post(
    "/projects/{project_id}/layout",
    response_model=LayoutPlan,
    tags=["projects"],
    status_code=201,
)
async def generate_layout(project_id: str) -> LayoutPlan:
    project = await get_project(project_id)
    layout = propose_layout(ProjectRequest(**project.dict(exclude={"id", "layout", "skeleton", "estimate", "execution_plan"})))
    project.layout = layout
    PROJECTS[project.id] = project
    return layout


@router.post(
    "/projects/{project_id}/structure",
    response_model=StructuralSkeleton,
    tags=["projects"],
    status_code=201,
)
async def generate_structure(project_id: str) -> StructuralSkeleton:
    project = await get_project(project_id)
    skeleton = derive_structure(project)
    project.skeleton = skeleton
    PROJECTS[project.id] = project
    return skeleton


@router.post(
    "/projects/{project_id}/estimate",
    response_model=Project,
    tags=["projects"],
    status_code=201,
)
async def generate_estimate(project_id: str) -> Project:
    project = await get_project(project_id)
    project.estimate = estimate_cost(project)
    project.execution_plan = execution_plan(project)
    PROJECTS[project.id] = project
    return project
