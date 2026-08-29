from datetime import date
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field


class AssetCreate(BaseModel):
    assetCode: str
    type: str
    name: str
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    location: str | None = None
    district: str | None = None
    constructionYear: int | None = None
    lengthKm: float | None = None
    projectCost: Decimal | None = None
    contractorId: str | None = None
    healthScore: float | None = None
    riskScore: float | None = None
    status: str | None = None
    lastInspection: date | None = None


class AssetUpdate(BaseModel):
    assetCode: str | None = None
    type: str | None = None
    name: str | None = None
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    location: str | None = None
    district: str | None = None
    constructionYear: int | None = None
    lengthKm: float | None = None
    projectCost: Decimal | None = None
    contractorId: str | None = None
    healthScore: float | None = None
    riskScore: float | None = None
    status: str | None = None
    lastInspection: date | None = None


class AssetOut(BaseModel):
    id: str
    assetCode: str
    type: str
    name: str
    location: str | None
    latitude: float
    longitude: float
    district: str | None
    constructionYear: int | None
    lengthKm: float | None
    projectCost: Decimal | None
    contractorId: str | None
    healthScore: float | None
    riskScore: float | None
    status: str | None
    lastInspection: date | None


class MaintenanceOut(BaseModel):
    id: str
    assetId: str
    date: date
    type: str
    detail: str
