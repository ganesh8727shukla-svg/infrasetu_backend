from datetime import date
from pydantic import BaseModel


class SatelliteOut(BaseModel):
    assetId: str
    developmentStatus: str | None
    changeDetection: str | None
    environmentalRisk: str | None
    lastObservation: date | None
    timeline: list[dict]


class SatelliteHistoryOut(BaseModel):
    year: str
    label: str
    note: str
