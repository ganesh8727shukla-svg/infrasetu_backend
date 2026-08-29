from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Asset, Complaint, AIDetection, RiskScore
from app.services.ids import new_id


def calculate_asset_risk(db: Session, asset: Asset) -> RiskScore:
    latest = db.execute(
        select(AIDetection)
        .where(AIDetection.asset_id == asset.id)
        .order_by(AIDetection.created_at.desc())
        .limit(1)
    ).scalar_one_or_none()

    complaint_count = db.scalar(
        select(func.count(Complaint.id)).where(Complaint.asset_id == asset.id)
    ) or 0

    ai_score = latest.confidence if latest else 0.0
    age = max(0, datetime.now(timezone.utc).year - (asset.construction_year or datetime.now().year))
    age_score = min(age * 3, 30)
    complaint_score = min(complaint_count * 2, 20)
    severity_bonus = 15 if latest and latest.severity.lower() == "critical" else 5 if latest else 0

    score = min(100.0, round(ai_score * 0.45 + age_score + complaint_score + severity_bonus, 2))
    level = "critical" if score >= 70 else "high" if score >= 50 else "moderate"

    factors = [
        {"label": "AI severity", "value": f"{ai_score:.0f}"},
        {"label": "Asset age", "value": f"{age} years"},
        {"label": "Complaint volume", "value": str(complaint_count)},
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
