from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import require_roles
from app.db.session import get_db
from app.models import AuditLog, User
from app.schemas.audit import AuditOut

router = APIRouter(prefix="/audit", tags=["Audit"])


def serialize(a: AuditLog) -> AuditOut:
    return AuditOut(
        id=a.id, timestamp=a.timestamp, assetId=a.asset_id,
        actorType=a.actor_type, actorId=a.actor_id, eventType=a.event_type,
        description=a.description, systemDecision=a.system_decision,
        metadata=a.metadata or {},
    )


@router.get("", response_model=list[AuditOut])
def list_audit(
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin")),
):
    return [serialize(a) for a in db.scalars(select(AuditLog).order_by(AuditLog.timestamp.desc())).all()]


@router.get("/{audit_id}", response_model=AuditOut)
def get_audit(
    audit_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin")),
):
    a = db.get(AuditLog, audit_id)
    if not a:
        raise HTTPException(404, "Audit log not found")
    return serialize(a)
