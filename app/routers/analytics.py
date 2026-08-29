from collections import defaultdict

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.deps import require_roles
from app.db.session import get_db
from app.models import Asset, Complaint, WorkOrder, User
from app.schemas.analytics import OverviewOut, HealthOut, RiskAnalyticsOut, WorkOrderAnalyticsOut

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/overview", response_model=OverviewOut)
def overview(db: Session = Depends(get_db), _: User = Depends(require_roles("admin"))):
    total = db.scalar(select(func.count(Asset.id))) or 0
    healthy = db.scalar(select(func.count(Asset.id)).where(Asset.health_score >= 70)) or 0
    high = db.scalar(select(func.count(Asset.id)).where(Asset.risk_score >= 50, Asset.risk_score < 70)) or 0
    critical = db.scalar(select(func.count(Asset.id)).where(Asset.risk_score >= 70)) or 0
    active = db.scalar(
        select(func.count(WorkOrder.id)).where(WorkOrder.status.in_(["Pending", "In Progress"]))
    ) or 0
    pending = db.scalar(
        select(func.count(WorkOrder.id)).where(WorkOrder.verification_status != "Verified")
    ) or 0
    pct = lambda n: round((n / total * 100), 1) if total else 0.0
    return OverviewOut(
        totalAssets=total, totalTrend="0%",
        healthy=healthy, healthyPct=pct(healthy),
        highRisk=high, highRiskPct=pct(high),
        critical=critical, criticalPct=pct(critical),
        activeWorkOrders=active, pendingVerification=pending,
    )


@router.get("/health", response_model=HealthOut)
def health(db: Session = Depends(get_db), _: User = Depends(require_roles("admin"))):
    rows = db.execute(
        select(Asset.health_score, func.count(Asset.id)).group_by(Asset.health_score)
    ).all()
    distribution = [{"name": "Healthy", "value": 0}, {"name": "At Risk", "value": 0}, {"name": "Critical", "value": 0}]
    for score, count in rows:
        if score is None:
            continue
        target = 0 if score >= 70 else 1 if score >= 40 else 2
        distribution[target]["value"] += count
    return HealthOut(distribution=distribution, trend=[])


@router.get("/risk", response_model=RiskAnalyticsOut)
def risk(db: Session = Depends(get_db), _: User = Depends(require_roles("admin"))):
    rows = db.execute(
        select(Asset.district, Asset.risk_score).where(Asset.district.is_not(None))
    ).all()
    grouped = defaultdict(lambda: {"district": "", "critical": 0, "high": 0, "moderate": 0})
    for district, score in rows:
        item = grouped[district]
        item["district"] = district
        if score is not None and score >= 70:
            item["critical"] += 1
        elif score is not None and score >= 50:
            item["high"] += 1
        else:
            item["moderate"] += 1
    return RiskAnalyticsOut(byDistrict=list(grouped.values()))


@router.get("/work-orders", response_model=WorkOrderAnalyticsOut)
def work_order_analytics(
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin")),
):
    total = db.scalar(select(func.count(WorkOrder.id))) or 0
    verified = db.scalar(
        select(func.count(WorkOrder.id)).where(WorkOrder.verification_status == "Verified")
    ) or 0
    return WorkOrderAnalyticsOut(
        trend=[],
        verificationRate=round(verified / total * 100, 1) if total else 0.0,
        repairTime=0.0,
        expenditure=[],
    )
