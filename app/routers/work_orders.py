from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_roles
from app.db.session import get_db
from app.models import Contractor, User, WorkOrder
from app.schemas.work_order import WorkOrderCreate, WorkOrderOut, WorkOrderUpdate
from app.services.audit_service import audit
from app.services.ids import new_id

router = APIRouter(prefix="/work-orders", tags=["Work Orders"])


def serialize(w: WorkOrder) -> WorkOrderOut:
    return WorkOrderOut(
        id=w.id, assetId=w.asset_id, complaintId=w.complaint_id,
        contractorId=w.contractor_id, issue=w.issue,
        requiredAction=w.required_action, priority=w.priority,
        status=w.status, riskScore=w.risk_score, createdAt=w.created_at,
        deadline=w.deadline, beforeImage=w.before_image, afterImage=w.after_image,
        notes=w.notes, verificationStatus=w.verification_status,
        verificationConfidence=w.verification_confidence,
    )


@router.get("", response_model=list[WorkOrderOut])
def list_work_orders(
    status: str | None = None,
    priority: str | None = None,
    contractorId: str | None = Query(default=None),
    assetId: str | None = Query(default=None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    stmt = select(WorkOrder).order_by(WorkOrder.created_at.desc())
    if user.role == "contractor":
        contractor = db.scalar(select(Contractor).where(Contractor.user_id == user.id))
        if not contractor:
            return []
        stmt = stmt.where(WorkOrder.contractor_id == contractor.id)
    elif user.role != "admin":
        raise HTTPException(403, "Insufficient permissions")
    elif contractorId:
        stmt = stmt.where(WorkOrder.contractor_id == contractorId)
    if status:
        stmt = stmt.where(WorkOrder.status == status)
    if priority:
        stmt = stmt.where(WorkOrder.priority == priority)
    if assetId:
        stmt = stmt.where(WorkOrder.asset_id == assetId)
    return [serialize(w) for w in db.scalars(stmt).all()]


@router.get("/{work_order_id}", response_model=WorkOrderOut)
def get_work_order(
    work_order_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    w = db.get(WorkOrder, work_order_id)
    if not w:
        raise HTTPException(404, "Work order not found")
    if user.role == "contractor":
        contractor = db.scalar(select(Contractor).where(Contractor.user_id == user.id))
        if not contractor or w.contractor_id != contractor.id:
            raise HTTPException(403, "Work order is not assigned to you")
    elif user.role != "admin":
        raise HTTPException(403, "Insufficient permissions")
    return serialize(w)


@router.post("", response_model=WorkOrderOut, status_code=201)
def create_work_order(
    payload: WorkOrderCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin")),
):
    if payload.contractorId and not db.get(Contractor, payload.contractorId):
        raise HTTPException(404, "Contractor not found")
    w = WorkOrder(
        id=new_id("WO"),
        asset_id=payload.assetId,
        complaint_id=payload.complaintId,
        contractor_id=payload.contractorId,
        issue=payload.issue,
        required_action=payload.requiredAction,
        priority=payload.priority,
        status="Pending",
        deadline=payload.deadline,
    )
    db.add(w)
    audit(
        db, actor_type="ADMIN", actor_id=_.id,
        event_type="WORK_ORDER_CREATED",
        description=f"Work order {w.id} created",
        asset_id=w.asset_id,
    )
    db.commit()
    db.refresh(w)
    return serialize(w)


@router.put("/{work_order_id}", response_model=WorkOrderOut)
def update_work_order(
    work_order_id: str,
    payload: WorkOrderUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    w = db.get(WorkOrder, work_order_id)
    if not w:
        raise HTTPException(404, "Work order not found")

    if user.role == "contractor":
        contractor = db.scalar(select(Contractor).where(Contractor.user_id == user.id))
        if not contractor or w.contractor_id != contractor.id:
            raise HTTPException(403, "Work order is not assigned to you")
        if payload.verificationStatus is not None or payload.verificationConfidence is not None:
            raise HTTPException(403, "Contractor cannot finalize verification")
    elif user.role != "admin":
        raise HTTPException(403, "Insufficient permissions")

    data = payload.model_dump(exclude_unset=True)

    if "status" in data:
        w.status = data["status"]
        if data["status"] == "In Progress":
            audit(db, actor_type="CONTRACTOR", actor_id=user.id,
                  event_type="WORK_STARTED", description=f"{w.id} started", asset_id=w.asset_id)

    if "beforeImage" in data:
        w.before_image = data["beforeImage"]
    if "afterImage" in data:
        w.after_image = data["afterImage"]
    if "notes" in data:
        w.notes = data["notes"]
    if any(k in data for k in ("beforeImage", "afterImage", "notes")):
        w.verification_status = "Analysing"
        audit(db, actor_type="CONTRACTOR", actor_id=user.id,
              event_type="REPAIR_EVIDENCE_SUBMITTED",
              description=f"Evidence submitted for {w.id}", asset_id=w.asset_id)

    if "verificationStatus" in data:
        w.verification_status = data["verificationStatus"]
    if "verificationConfidence" in data:
        w.verification_confidence = data["verificationConfidence"]
    if "verificationStatus" in data or "verificationConfidence" in data:
        audit(db, actor_type="ADMIN", actor_id=user.id,
              event_type="WORK_ORDER_VERIFIED",
              description=f"Verification updated for {w.id}", asset_id=w.asset_id)

    db.commit()
    db.refresh(w)
    return serialize(w)
