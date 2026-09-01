from datetime import date
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from geoalchemy2 import functions as geofunc
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import require_roles
from app.db.session import get_db
from app.models import Asset, MaintenanceHistory, User
from app.schemas.asset import (
    AssetCreate,
    AssetOut,
    AssetUpdate,
    MaintenanceOut,
)
from app.services.geo import point
from app.services.ids import new_id


router = APIRouter(
    prefix="/assets",
    tags=["Assets"],
)


def to_asset(db: Session, a: Asset) -> AssetOut:
    lon, lat = db.execute(
        select(
            geofunc.ST_X(a.geom),
            geofunc.ST_Y(a.geom),
        )
    ).one()

    return AssetOut(
        id=a.id,
        assetCode=a.asset_code,
        type=a.type,
        name=a.name,
        location=a.location,
        latitude=float(lat),
        longitude=float(lon),
        district=a.district,
        constructionYear=a.construction_year,
        lengthKm=a.length_km,
        projectCost=a.project_cost,
        contractorId=a.contractor_id,
        healthScore=a.health_score,
        riskScore=a.risk_score,
        status=a.status,
        lastInspection=a.last_inspection,
    )


# -------------------------------------------------------------------
# READ ASSETS
# Admin + Citizen can view infrastructure assets.
# -------------------------------------------------------------------

@router.get(
    "",
    response_model=list[AssetOut],
)
def list_assets(
    search: str | None = None,
    type: str | None = None,
    risk: str | None = Query(default=None),
    db: Session = Depends(get_db),
    _: User = Depends(
        require_roles("admin", "citizen")
    ),
):
    stmt = select(Asset).order_by(Asset.id)

    if search:
        stmt = stmt.where(
            Asset.name.ilike(f"%{search}%")
        )

    if type:
        stmt = stmt.where(
            Asset.type == type
        )

    rows = db.scalars(stmt).all()

    if risk:
        risk = risk.lower()

        rows = [
            a
            for a in rows
            if (
                a.risk_score or 0
            )
            >= (
                70
                if risk == "critical"
                else 50
                if risk == "high"
                else 0
            )
        ]

    return [
        to_asset(db, a)
        for a in rows
    ]


# -------------------------------------------------------------------
# READ SINGLE ASSET
# Admin + Citizen can view an individual asset.
# -------------------------------------------------------------------

@router.get(
    "/{asset_id}",
    response_model=AssetOut,
)
def get_asset(
    asset_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(
        require_roles("admin", "citizen")
    ),
):
    asset = db.get(
        Asset,
        asset_id,
    )

    if not asset:
        raise HTTPException(
            status_code=404,
            detail="Asset not found",
        )

    return to_asset(
        db,
        asset,
    )


# -------------------------------------------------------------------
# CREATE ASSET
# Admin only.
# -------------------------------------------------------------------

@router.post(
    "",
    response_model=AssetOut,
    status_code=201,
)
def create_asset(
    payload: AssetCreate,
    db: Session = Depends(get_db),
    _: User = Depends(
        require_roles("admin")
    ),
):
    if db.scalar(
        select(Asset).where(
            Asset.asset_code
            == payload.assetCode
        )
    ):
        raise HTTPException(
            status_code=409,
            detail="assetCode already exists",
        )

    asset = Asset(
        id=new_id("AST"),
        asset_code=payload.assetCode,
        type=payload.type,
        name=payload.name,
        location=payload.location,
        geom=point(
            payload.longitude,
            payload.latitude,
        ),
        district=payload.district,
        construction_year=payload.constructionYear,
        length_km=payload.lengthKm,
        project_cost=payload.projectCost,
        contractor_id=payload.contractorId,
        health_score=payload.healthScore,
        risk_score=payload.riskScore,
        status=payload.status,
        last_inspection=payload.lastInspection,
    )

    db.add(asset)
    db.commit()
    db.refresh(asset)

    return to_asset(
        db,
        asset,
    )


# -------------------------------------------------------------------
# UPDATE ASSET
# Admin only.
# -------------------------------------------------------------------

@router.put(
    "/{asset_id}",
    response_model=AssetOut,
)
def update_asset(
    asset_id: str,
    payload: AssetUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(
        require_roles("admin")
    ),
):
    asset = db.get(
        Asset,
        asset_id,
    )

    if not asset:
        raise HTTPException(
            status_code=404,
            detail="Asset not found",
        )

    data = payload.model_dump(
        exclude_unset=True
    )

    if "assetCode" in data:
        asset.asset_code = data[
            "assetCode"
        ]

    for source, target in [
        ("type", "type"),
        ("name", "name"),
        ("location", "location"),
        ("district", "district"),
        (
            "constructionYear",
            "construction_year",
        ),
        ("lengthKm", "length_km"),
        ("projectCost", "project_cost"),
        ("contractorId", "contractor_id"),
        ("healthScore", "health_score"),
        ("riskScore", "risk_score"),
        ("status", "status"),
        (
            "lastInspection",
            "last_inspection",
        ),
    ]:
        if source in data:
            setattr(
                asset,
                target,
                data[source],
            )

    if (
        "latitude" in data
        or "longitude" in data
    ):
        lon, lat = db.execute(
            select(
                geofunc.ST_X(asset.geom),
                geofunc.ST_Y(asset.geom),
            )
        ).one()

        asset.geom = point(
            data.get(
                "longitude",
                float(lon),
            ),
            data.get(
                "latitude",
                float(lat),
            ),
        )

    db.commit()
    db.refresh(asset)

    return to_asset(
        db,
        asset,
    )


# -------------------------------------------------------------------
# MAINTENANCE HISTORY
# Admin only.
# -------------------------------------------------------------------

@router.get(
    "/{asset_id}/maintenance",
    response_model=list[MaintenanceOut],
)
def maintenance_history(
    asset_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(
        require_roles("admin")
    ),
):
    if not db.get(
        Asset,
        asset_id,
    ):
        raise HTTPException(
            status_code=404,
            detail="Asset not found",
        )

    rows = db.scalars(
        select(MaintenanceHistory)
        .where(
            MaintenanceHistory.asset_id
            == asset_id
        )
        .order_by(
            MaintenanceHistory.date.desc()
        )
    ).all()

    return [
        MaintenanceOut(
            id=r.id,
            assetId=r.asset_id,
            date=r.date,
            type=r.type,
            detail=r.detail,
        )
        for r in rows
    ]