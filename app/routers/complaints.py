from fastapi import APIRouter, Depends, HTTPException, Query
from geoalchemy2 import functions as geofunc
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_roles
from app.db.session import get_db
from app.models import Complaint, User, Asset
from app.schemas.complaint import ComplaintCreate, ComplaintOut
from app.services.audit_service import audit
from app.services.geo import point
from app.services.ids import new_id
from app.services.pipeline_service import run_complaint_pipeline

router = APIRouter(prefix="/complaints", tags=["Complaints"])


def serialize(db, c: Complaint) -> ComplaintOut:
    lon, lat = db.execute(select(geofunc.ST_X(c.geom), geofunc.ST_Y(c.geom))).one()
    return ComplaintOut(
        id=c.id, assetId=c.asset_id, citizenId=c.citizen_id,
        issueType=c.issue_type, description=c.description, aiStatus=c.ai_status,
        riskScore=c.risk_score, status=c.status, submittedBy=c.citizen.name,
        latitude=float(lat), longitude=float(lon), imageUrl=c.image_url,
        createdAt=c.created_at, workOrderId=c.work_order_id,
    )


@router.get("", response_model=list[ComplaintOut])
def list_complaints(
    status: str | None = None,
    citizenId: str | None = Query(default=None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    stmt = select(Complaint).order_by(Complaint.created_at.desc())
    if user.role == "citizen":
        stmt = stmt.where(Complaint.citizen_id == user.id)
    elif user.role != "admin":
        raise HTTPException(403, "Insufficient permissions")
    elif citizenId:
        stmt = stmt.where(Complaint.citizen_id == citizenId)
    if status:
        stmt = stmt.where(Complaint.status == status)
    return [serialize(db, c) for c in db.scalars(stmt).all()]


@router.get("/{complaint_id}", response_model=ComplaintOut)
def get_complaint(
    complaint_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    c = db.get(Complaint, complaint_id)
    if not c:
        raise HTTPException(404, "Complaint not found")
    if user.role == "citizen" and c.citizen_id != user.id:
        raise HTTPException(403, "Not your complaint")
    if user.role not in {"admin", "citizen"}:
        raise HTTPException(403, "Insufficient permissions")
    return serialize(db, c)


@router.post("", response_model=ComplaintOut, status_code=201)
def create_complaint(
    payload: ComplaintCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("citizen")),
):
    if not db.get(Asset, payload.assetId):
        raise HTTPException(404, "Asset not found")
    c = Complaint(
        id=new_id("CMP"),
        asset_id=payload.assetId,
        citizen_id=user.id,
        issue_type=payload.issueType,
        description=payload.description,
        geom=point(payload.longitude, payload.latitude),
        image_url=payload.imageUrl,
        ai_status="Pending",
        status="Reported",
    )
    db.add(c)
    db.flush()
    try:
        run_complaint_pipeline(db, c)
        audit(
            db,
            actor_type="AUTOMATED SYSTEM",
            actor_id="AI-ENGINE",
            event_type="COMPLAINT_PIPELINE_COMPLETED",
            description=f"Complaint {c.id} processed",
            asset_id=c.asset_id,
            system_decision="AI → RISK → WORK ORDER",
            metadata={"complaintId": c.id, "risk": c.risk_score},
        )
        db.commit()
    except Exception:
        db.rollback()
        raise
    db.refresh(c)
    return serialize(db, c)
