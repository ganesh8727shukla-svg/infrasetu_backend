from datetime import date, datetime
from pydantic import BaseModel


class WorkOrderCreate(BaseModel):
    assetId: str
    contractorId: str | None = None
    complaintId: str | None = None
    issue: str
    requiredAction: str
    priority: str = "Moderate"
    deadline: date | None = None


class WorkOrderUpdate(BaseModel):
    status: str | None = None
    beforeImage: str | None = None
    afterImage: str | None = None
    notes: str | None = None
    verificationStatus: str | None = None
    verificationConfidence: float | None = None


class WorkOrderOut(BaseModel):
    id: str
    assetId: str
    complaintId: str | None
    contractorId: str | None
    issue: str
    requiredAction: str
    priority: str
    status: str
    riskScore: float | None
    createdAt: datetime
    deadline: date | None
    beforeImage: str | None
    afterImage: str | None
    notes: str | None
    verificationStatus: str
    verificationConfidence: float | None
