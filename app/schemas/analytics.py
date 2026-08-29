from pydantic import BaseModel


class OverviewOut(BaseModel):
    totalAssets: int
    totalTrend: str
    healthy: int
    healthyPct: float
    highRisk: int
    highRiskPct: float
    critical: int
    criticalPct: float
    activeWorkOrders: int
    pendingVerification: int


class HealthOut(BaseModel):
    distribution: list[dict]
    trend: list[dict]


class RiskAnalyticsOut(BaseModel):
    byDistrict: list[dict]


class WorkOrderAnalyticsOut(BaseModel):
    trend: list[dict]
    verificationRate: float
    repairTime: float
    expenditure: list[dict]
