from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import require_roles
from app.db.session import get_db
from app.models import Asset, AIDetection, User
from app.schemas.ai import (
    AIAnalyzeRequest,
    AIAnalyzeResponse,
    AIDetectionOut,
)
from app.services.ai_service import analyze_image


router = APIRouter(prefix="/ai", tags=["AI"])


@router.post(
    "/analyze",
    response_model=AIAnalyzeResponse,
)
def analyze(
    payload: AIAnalyzeRequest,
    db: Session = Depends(get_db),
    user: User = Depends(
        require_roles("citizen", "admin")
    ),
):
    # Check that the requested asset exists
    if not db.get(Asset, payload.assetId):
        raise HTTPException(
            status_code=404,
            detail="Asset not found",
        )

    # Run AI analysis
    rows = analyze_image(
        db,
        asset_id=payload.assetId,
        image_url=payload.imageUrl,
    )

    # Save AI detections
    db.commit()

    # Refresh database-generated fields
    for row in rows:
        db.refresh(row)

    # Convert database rows to API response objects
    detections = [
        AIDetectionOut(
            id=row.id,
            assetId=row.asset_id,
            detectionType=row.detection_type,
            confidence=row.confidence,
            severity=row.severity,
            imageUrl=row.image_url,
            createdAt=row.created_at,
        )
        for row in rows
    ]

    return AIAnalyzeResponse(
        detections=detections,
        totalDetections=len(detections),
    )


@router.get(
    "/detections/{asset_id}",
    response_model=list[AIDetectionOut],
)
def detections(
    asset_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(
        require_roles("admin")
    ),
):
    rows = db.scalars(
        select(AIDetection)
        .where(
            AIDetection.asset_id == asset_id
        )
        .order_by(
            AIDetection.created_at.desc()
        )
    ).all()

    return [
        AIDetectionOut(
            id=r.id,
            assetId=r.asset_id,
            detectionType=r.detection_type,
            confidence=r.confidence,
            severity=r.severity,
            imageUrl=r.image_url,
            createdAt=r.created_at,
        )
        for r in rows
    ]