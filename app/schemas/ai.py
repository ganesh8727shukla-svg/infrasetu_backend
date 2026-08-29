from datetime import datetime
from pydantic import BaseModel, Field


class AIAnalyzeRequest(BaseModel):
    assetId: str
    imageUrl: str


class AIDetectionOut(BaseModel):
    id: str
    assetId: str
    detectionType: str
    confidence: float
    severity: str
    imageUrl: str
    createdAt: datetime
