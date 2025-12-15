from __future__ import annotations

import uuid
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, validator


class RoomSpec(BaseModel):
    """Represents a single room or space in an architectural layout."""

    name: str
    area_m2: float
    notes: Optional[str] = None


class LayoutPlan(BaseModel):
    """AI-assisted layout proposal derived from the requirement brief."""

    efficiency: float = Field(..., description="Net to gross efficiency ratio")
    gross_area_m2: float = Field(..., description="Total built-up area considered")
    circulation_m2: float = Field(..., description="Area reserved for circulation/services")
    rooms: List[RoomSpec] = Field(default_factory=list)
    staircase: str = Field(..., description="Chosen staircase archetype")
    parking_stalls: int = Field(0, description="Number of parking bays provisioned")


class StructuralSkeleton(BaseModel):
    """Simplified structural understanding as a precursor to solver export."""

    columns: int
    beams: int
    slab_type: str
    foundation: str
    seismic_zone: str
    wind_zone: str
    notes: List[str] = Field(default_factory=list)


class EstimateLine(BaseModel):
    """Single BOQ/estimation line item."""

    category: str
    description: str
    unit: str
    quantity: float
    rate: float

    @property
    def amount(self) -> float:
        return self.quantity * self.rate


class EstimateSummary(BaseModel):
    """SSR/SOR based estimation summary."""

    base_cost: float
    contingency_pct: float
    gst_pct: float
    total: float
    lines: List[EstimateLine]


class ExecutionTask(BaseModel):
    """High-level project execution step."""

    name: str
    duration_days: int
    dependencies: List[str] = Field(default_factory=list)


class ProjectRequest(BaseModel):
    """Incoming requirement payload used to seed the unified data model."""

    title: str
    location: str
    usage: str = Field(..., description="residential/industrial/commercial")
    floors: int = Field(..., ge=1, description="Number of storeys")
    footprint_m2: float = Field(..., gt=0)
    preferred_codes: List[str] = Field(default_factory=list)
    structure_types: List[str] = Field(default_factory=list)
    soil_type: Optional[str] = None
    budget: Optional[float] = None
    regional_rate: Optional[str] = Field(
        None,
        description="Regional SSR/SOR key (e.g., telangana-2024)",
    )


class Project(BaseModel):
    """Aggregate view of the project across requirement, layout, structure, and costing."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    location: str
    usage: str
    floors: int
    footprint_m2: float
    preferred_codes: List[str] = Field(default_factory=list)
    structure_types: List[str] = Field(default_factory=list)
    soil_type: Optional[str] = None
    budget: Optional[float] = None
    regional_rate: Optional[str] = None
    layout: Optional[LayoutPlan] = None
    skeleton: Optional[StructuralSkeleton] = None
    estimate: Optional[EstimateSummary] = None
    execution_plan: List[ExecutionTask] = Field(default_factory=list)

    @validator("preferred_codes", "structure_types", pre=True)
    def dedupe_values(cls, value: List[str]) -> List[str]:
        if not value:
            return []
        seen: Dict[str, str] = {}
        for item in value:
            seen[item.lower()] = item
        return list(seen.values())
