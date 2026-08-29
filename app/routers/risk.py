from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import require_roles
from app.db.session import get_db
from app.models import Alert, Asset, User
from app.schemas.risk import AlertOut, RiskOut
from app.services.risk_service import calculate_asset_risk

router = APIRouter(prefix="/risk", tags=["Risk"])


@router.get("/critical", response_model=list[AlertOut])
def critical_alerts(
    resolved: bool | None = None,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin")),
):
    stmt = select(Alert).where(Alert.level == "critical").order_by(Alert.created_at.desc())
    if resolved is not None:
        stmt = stmt.where(Alert.resolved == resolved)
    rows = db.scalars(stmt).all()
    return [
        AlertOut(
            id=a.id, assetId=a.asset_id, level=a.level, riskScore=a.risk_score,
            issue=a.issue, aiConfidence=a.ai_confidence,
            recommendedAction=a.recommended_action, createdAt=a.created_at,
            resolved=a.resolved, workOrderId=a.work_order_id,
        )
        for a in rows
    ]


@router.get("/{asset_id}", response_model=RiskOut)
def asset_risk(
    asset_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin")),
):
    asset = db.get(Asset, asset_id)
    if not asset:
        raise HTTPException(404, "Asset not found")
    risk = calculate_asset_risk(db, asset)
    db.commit()
    db.refresh(risk)
    return RiskOut(
        assetId=asset.id, score=risk.score, level=risk.level,
        factors=risk.factors, calculatedAt=risk.calculated_at,
    )
