from pydantic import BaseModel


class ContractorOut(BaseModel):
    id: str
    name: str
    licenseStatus: str
    district: str | None
    activeOrders: int
    completedOrders: int
    averageCompletionDays: float
    performanceScore: float
    verificationRate: float
    repeatDamageRate: float
