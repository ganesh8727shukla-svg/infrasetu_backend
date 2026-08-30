from datetime import datetime

from pydantic import BaseModel


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


class AIAnalyzeResponse(BaseModel):
    detections: list[AIDetectionOut]
    totalDetections: int
