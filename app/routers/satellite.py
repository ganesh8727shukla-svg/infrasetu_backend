from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import require_roles
from app.db.session import get_db
from app.models import SatelliteRecord, SatelliteObservation, Asset, User
from app.schemas.satellite import SatelliteHistoryOut, SatelliteOut

router = APIRouter(prefix="/satellite", tags=["Satellite"])


@router.get("/{asset_id}", response_model=SatelliteOut)
def satellite(
    asset_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin")),
):
    record = db.scalar(select(SatelliteRecord).where(SatelliteRecord.asset_id == asset_id))
    if not record:
        raise HTTPException(404, "Satellite record not found")
    timeline = [
        {"year": x.year, "label": x.label, "note": x.note}
        for x in sorted(record.observations, key=lambda x: x.year)
    ]
    return SatelliteOut(
        assetId=record.asset_id,
        developmentStatus=record.development_status,
        changeDetection=record.change_detection,
        environmentalRisk=record.environmental_risk,
        lastObservation=record.last_observation,
        timeline=timeline,
    )


@router.get("/{asset_id}/history", response_model=list[SatelliteHistoryOut])
def history(
    asset_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin")),
):
    record = db.scalar(select(SatelliteRecord).where(SatelliteRecord.asset_id == asset_id))
    if not record:
        raise HTTPException(404, "Satellite record not found")
    return [
        SatelliteHistoryOut(year=x.year, label=x.label, note=x.note)
        for x in sorted(record.observations, key=lambda x: x.year)
    ]
