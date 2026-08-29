from datetime import datetime
from pydantic import BaseModel, Field


class ComplaintCreate(BaseModel):
    assetId: str
    issueType: str
    description: str = Field(min_length=1)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    imageUrl: str | None = None


class ComplaintOut(BaseModel):
    id: str
    assetId: str
    citizenId: str
    issueType: str
    description: str
    aiStatus: str
    riskScore: float | None
    status: str
    submittedBy: str
    latitude: float
    longitude: float
    imageUrl: str | None
    createdAt: datetime
    workOrderId: str | None = None
