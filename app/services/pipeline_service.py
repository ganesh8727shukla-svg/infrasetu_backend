from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.models import Alert, Complaint, WorkOrder, Contractor, User
from app.services.ai_service import analyze_image
from app.services.risk_service import calculate_asset_risk
from app.services.ids import new_id


def run_complaint_pipeline(db: Session, complaint: Complaint):
    """
    Server-side replacement for the frontend mock `runAutomatedPipeline`.

    complaint -> AI -> risk -> alert -> work order -> audit.
    """
    complaint.ai_status = "Analysing"
    db.flush()

    detection = None
    if complaint.image_url:
        detection = analyze_image(
            db,
            asset_id=complaint.asset_id,
            image_url=complaint.image_url,
            complaint_id=complaint.id,
        )
        db.flush()

    complaint.ai_status = "Completed"
    risk = calculate_asset_risk(db, complaint.asset)
    db.flush()

    complaint.risk_score = risk.score

    contractor = db.execute(
        __import__("sqlalchemy").select(Contractor)
        .order_by(Contractor.active_orders.asc())
        .limit(1)
    ).scalar_one_or_none()

    work_order = None
    if risk.score >= 70:
        work_order = WorkOrder(
            id=new_id("WO"),
            asset_id=complaint.asset_id,
            complaint_id=complaint.id,
            contractor_id=contractor.id if contractor else None,
            issue=complaint.issue_type,
            required_action="Dispatch emergency repair",
            priority="Critical",
            status="Pending",
            risk_score=risk.score,
            deadline=date.today() + timedelta(days=2),
        )
        db.add(work_order)
        db.flush()
        complaint.work_order_id = work_order.id
        complaint.status = "Work Order Created"

        alert = Alert(
            id=new_id("ALR"),
            asset_id=complaint.asset_id,
            work_order_id=work_order.id,
            level=risk.level,
            risk_score=risk.score,
            issue=complaint.issue_type,
            ai_confidence=detection.confidence if detection else None,
            recommended_action="Dispatch emergency repair",
        )
        db.add(alert)
    else:
        complaint.status = "Under Assessment"

    return detection, risk, work_order
