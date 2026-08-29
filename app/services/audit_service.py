from sqlalchemy.orm import Session

from app.models import AuditLog
from app.services.ids import new_id


def audit(
    db: Session,
    *,
    actor_type: str,
    actor_id: str,
    event_type: str,
    description: str,
    asset_id: str | None = None,
    system_decision: str | None = None,
    metadata: dict | None = None,
):
    row = AuditLog(
        id=new_id("AUD"),
        actor_type=actor_type,
        actor_id=actor_id,
        event_type=event_type,
        description=description,
        asset_id=asset_id,
        system_decision=system_decision,
        metadata=metadata or {},
    )
    db.add(row)
    return row
