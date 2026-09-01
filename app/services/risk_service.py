from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Asset, Complaint, AIDetection, RiskScore
from app.services.ids import new_id


def calculate_asset_risk(
    db: Session,
    asset: Asset,
) -> RiskScore:
    complaints = db.scalars(
        select(Complaint)
        .where(Complaint.asset_id == asset.id)
        .order_by(Complaint.created_at.desc())
    ).all()

    complaint_count = len(complaints)

    current_complaint_id = (
        complaints[0].id
        if complaints
        else None
    )

    if current_complaint_id:
        detections = db.scalars(
            select(AIDetection)
            .where(
                AIDetection.asset_id == asset.id,
                AIDetection.complaint_id == current_complaint_id,
            )
            .order_by(AIDetection.created_at.desc())
        ).all()
    else:
        detections = []

    highest_confidence = (
        max(float(d.confidence) for d in detections)
        if detections
        else 0.0
    )

    severity_weights = {
        "low": 10,
        "medium": 30,
        "high": 60,
        "critical": 100,
    }

    strongest_severity_score = 0.0

    for detection in detections:
        severity = (
            detection.severity or "low"
        ).lower()

        strongest_severity_score = max(
            strongest_severity_score,
            severity_weights.get(severity, 10),
        )

    detection_count = len(detections)

    detection_density_score = min(
        detection_count * 3,
        20,
    )

    current_year = datetime.now(
        timezone.utc
    ).year

    if asset.construction_year:
        age = max(
            0,
            current_year - asset.construction_year,
        )
        age_score = min(
            age * 1.5,
            15,
        )
    else:
        age = None
        age_score = 0.0

    complaint_score = min(
        complaint_count * 5,
        15,
    )

    ai_evidence = (
        highest_confidence * 0.60
        + strongest_severity_score * 0.40
    )

    ai_evidence_score = min(
        ai_evidence * 0.50,
        50,
    )

    score = min(
        100.0,
        round(
            ai_evidence_score
            + detection_density_score
            + complaint_score
            + age_score,
            2,
        ),
    )

    if score >= 70:
        level = "critical"
    elif score >= 50:
        level = "high"
    else:
        level = "moderate"

    factors = [
        {
            "label": "AI confidence",
            "value": f"{highest_confidence:.0f}",
        },
        {
            "label": "Detected defects",
            "value": str(detection_count),
        },
        {
            "label": "Complaint volume",
            "value": str(complaint_count),
        },
        {
            "label": "Asset age",
            "value": (
                f"{age} years"
                if age is not None
                else "Unknown"
            ),
        },
    ]

    risk = RiskScore(
        id=new_id("RISK"),
        asset_id=asset.id,
        score=score,
        level=level,
        factors=factors,
    )

    asset.risk_score = score
    db.add(risk)

    return risk