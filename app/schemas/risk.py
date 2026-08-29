from datetime import datetime
from pydantic import BaseModel


class RiskFactor(BaseModel):
    label: str
    value: str


class RiskOut(BaseModel):
    assetId: str
    score: float
    level: str
    factors: list[RiskFactor]
    calculatedAt: datetime


class AlertOut(BaseModel):
    id: str
    assetId: str
    level: str
    riskScore: float
    issue: str
    aiConfidence: float | None
    recommendedAction: str
    createdAt: datetime
    resolved: bool
    workOrderId: str | None
