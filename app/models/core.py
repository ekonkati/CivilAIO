from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class ModuleDescriptor(BaseModel):
    """Describes a feature module exposed by the platform."""

    key: str = Field(..., description="Unique module identifier")
    name: str = Field(..., description="Human-readable module name")
    summary: str = Field(..., description="What the module provides")
    billing_model: str = Field(..., description="How the module is billed (per-use/subscription)")
    maturity: str = Field("planned", description="Delivery status: planned, mvp, beta, ga")


class RequirementBrief(BaseModel):
    """High-level project requirement captured from the user."""

    title: str
    location: Optional[str] = None
    description: Optional[str] = None
    preferred_codes: List[str] = Field(default_factory=list, description="Design codes requested")
    structure_types: List[str] = Field(default_factory=list, description="Structure types involved")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class HealthStatus(BaseModel):
    status: str = Field(..., description="Service health state")
    environment: str = Field(..., description="Environment label")
    version: str = Field(..., description="Application version")
    modules: List[ModuleDescriptor] = Field(default_factory=list)
