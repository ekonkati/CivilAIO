from __future__ import annotations

import math
from typing import Dict, List, Tuple

from app.models.project import (
    EstimateLine,
    EstimateSummary,
    ExecutionTask,
    LayoutPlan,
    Project,
    ProjectRequest,
    RoomSpec,
    StructuralSkeleton,
)


SSR_RATES: Dict[str, float] = {
    "telangana-2024": 21000.0,
    "andhra-2024": 20000.0,
    "default": 19500.0,
}

WIND_ZONES = {"coastal": "WL-6", "interior": "WL-3"}
SEISMIC_ZONES = {"north": "Zone V", "central": "Zone IV", "south": "Zone III"}


def _base_room_schedule(request: ProjectRequest) -> List[RoomSpec]:
    gross = request.footprint_m2 * request.floors
    bedrooms = max(2, round(gross / 55.0)) if request.usage == "residential" else 0
    offices = max(2, round(gross / 80.0)) if request.usage == "commercial" else 0
    stalls = max(1, round(gross / 120.0)) if request.usage == "industrial" else 0

    schedule: List[RoomSpec] = []
    if bedrooms:
        schedule.append(RoomSpec(name="Bedroom", area_m2=12.0, notes="Template sizing"))
        schedule.append(RoomSpec(name="Kitchen", area_m2=8.0))
        schedule.append(RoomSpec(name="Living", area_m2=18.0))
        schedule.append(RoomSpec(name="Toilet", area_m2=4.5))
    if offices:
        schedule.append(RoomSpec(name="Office", area_m2=16.0))
        schedule.append(RoomSpec(name="Meeting Room", area_m2=20.0))
        schedule.append(RoomSpec(name="Pantry", area_m2=6.0))
    if stalls:
        schedule.append(RoomSpec(name="Shop Floor", area_m2=50.0))
        schedule.append(RoomSpec(name="Warehouse", area_m2=80.0))
        schedule.append(RoomSpec(name="Utility", area_m2=15.0))

    return schedule


def propose_layout(request: ProjectRequest) -> LayoutPlan:
    gross = request.footprint_m2 * request.floors
    efficiency = 0.78 if request.usage == "residential" else 0.72
    circulation = gross * (1 - efficiency)
    rooms = _base_room_schedule(request)
    staircase = "doglegged" if request.floors <= 4 else "open-well"
    parking = max(1, math.ceil(request.footprint_m2 / 40.0)) if request.usage != "industrial" else 0

    return LayoutPlan(
        efficiency=round(efficiency, 2),
        gross_area_m2=round(gross, 2),
        circulation_m2=round(circulation, 2),
        rooms=rooms,
        staircase=staircase,
        parking_stalls=parking,
    )


def derive_structure(project: Project) -> StructuralSkeleton:
    columns = max(4, math.ceil(project.footprint_m2 / 25.0))
    beams = columns * 2
    slab_type = "two-way" if project.footprint_m2 / columns < 30 else "flat-slab"
    foundation = "isolated footings" if project.soil_type != "soft" else "raft"
    seismic_zone = SEISMIC_ZONES.get(_regional_bucket(project.location), "Zone III")
    wind_zone = WIND_ZONES.get(_wind_bucket(project.location), "WL-3")
    notes = [
        "Preliminary sizing only; hook to Kratos for solver export",
        "Code checks pending integration with IS/ACI/EC modules",
    ]

    return StructuralSkeleton(
        columns=columns,
        beams=beams,
        slab_type=slab_type,
        foundation=foundation,
        seismic_zone=seismic_zone,
        wind_zone=wind_zone,
        notes=notes,
    )


def _regional_bucket(location: str) -> str:
    loc_lower = location.lower()
    if any(key in loc_lower for key in ["delhi", "himalaya", "northeast"]):
        return "north"
    if any(key in loc_lower for key in ["mumbai", "chennai", "coast", "vishakh"]):
        return "coastal"
    return "south"


def _wind_bucket(location: str) -> str:
    loc_lower = location.lower()
    if any(key in loc_lower for key in ["coast", "bay", "mumbai", "chennai", "vizag"]):
        return "coastal"
    return "interior"


def estimate_cost(project: Project) -> EstimateSummary:
    rate = SSR_RATES.get(project.regional_rate or "", SSR_RATES["default"])
    builtup = project.footprint_m2 * project.floors
    base_cost = builtup * rate
    contingency_pct = 5.0
    gst_pct = 18.0
    contingency = base_cost * contingency_pct / 100
    gst = (base_cost + contingency) * gst_pct / 100
    total = base_cost + contingency + gst

    lines = [
        EstimateLine(
            category="civil",
            description="Concrete + masonry + finishing",
            unit="m2",
            quantity=round(builtup, 2),
            rate=rate,
        ),
        EstimateLine(
            category="steel",
            description="Rebar/structural steel allowance",
            unit="kg",
            quantity=round(builtup * 35, 2),
            rate=65.0,
        ),
        EstimateLine(
            category="formwork",
            description="Shuttering and staging",
            unit="m2",
            quantity=round(builtup, 2),
            rate=350.0,
        ),
    ]

    return EstimateSummary(
        base_cost=round(base_cost, 2),
        contingency_pct=contingency_pct,
        gst_pct=gst_pct,
        total=round(total, 2),
        lines=lines,
    )


def execution_plan(project: Project) -> List[ExecutionTask]:
    sequence: List[Tuple[str, int, List[str]]] = [
        ("Mobilization", 7, []),
        ("Foundations", 21, ["Mobilization"]),
        ("Superstructure", 45, ["Foundations"]),
        ("Roofing", 14, ["Superstructure"]),
        ("Finishes", 30, ["Roofing"]),
        ("Handover", 5, ["Finishes"]),
    ]
    return [ExecutionTask(name=name, duration_days=days, dependencies=deps) for name, days, deps in sequence]


def seed_project(request: ProjectRequest) -> Project:
    project = Project(**request.dict())
    project.layout = propose_layout(request)
    project.skeleton = derive_structure(project)
    project.estimate = estimate_cost(project)
    project.execution_plan = execution_plan(project)
    return project
