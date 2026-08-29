from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_roles
from app.db.session import get_db
from app.models import Contractor, User, WorkOrder
from app.schemas.contractor import ContractorOut

router = APIRouter(prefix="/contractors", tags=["Contractors"])


def serialize(c: Contractor) -> ContractorOut:
    return ContractorOut(
        id=c.id, name=c.name, licenseStatus=c.license_status,
        district=c.district, activeOrders=c.active_orders,
        completedOrders=c.completed_orders,
        averageCompletionDays=c.average_completion_days,
        performanceScore=c.performance_score,
        verificationRate=c.verification_rate,
        repeatDamageRate=c.repeat_damage_rate,
    )


@router.get("", response_model=list[ContractorOut])
def list_contractors(
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin")),
):
    return [serialize(c) for c in db.scalars(select(Contractor).order_by(Contractor.name)).all()]


@router.get("/{contractor_id}", response_model=ContractorOut)
def get_contractor(
    contractor_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    c = db.get(Contractor, contractor_id)
    if not c:
        raise HTTPException(404, "Contractor not found")
    if user.role == "contractor" and c.user_id != user.id:
        raise HTTPException(403, "Not your contractor profile")
    if user.role not in {"admin", "contractor"}:
        raise HTTPException(403, "Insufficient permissions")
    return serialize(c)
