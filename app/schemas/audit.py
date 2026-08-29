from datetime import datetime
from pydantic import BaseModel


class AuditOut(BaseModel):
    id: str
    timestamp: datetime
    assetId: str | None
    actorType: str
    actorId: str
    eventType: str
    description: str
    systemDecision: str | None
    metadata: dict
