from datetime import datetime, date
from decimal import Decimal

from geoalchemy2 import Geography
from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(150))
    role: Mapped[str] = mapped_column(String(30), index=True)
    organisation: Mapped[str | None] = mapped_column(String(200), nullable=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    contractor: Mapped["Contractor | None"] = relationship(back_populates="user", uselist=False)
    complaints: Mapped[list["Complaint"]] = relationship(
        back_populates="citizen", foreign_keys="Complaint.citizen_id"
    )
    notifications: Mapped[list["Notification"]] = relationship(back_populates="user")


class Contractor(Base):
    __tablename__ = "contractors"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), unique=True, nullable=True)
    name: Mapped[str] = mapped_column(String(200))
    license_status: Mapped[str] = mapped_column(String(40), default="ACTIVE")
    district: Mapped[str | None] = mapped_column(String(100), nullable=True)
    active_orders: Mapped[int] = mapped_column(Integer, default=0)
    completed_orders: Mapped[int] = mapped_column(Integer, default=0)
    average_completion_days: Mapped[float] = mapped_column(default=0)
    performance_score: Mapped[float] = mapped_column(default=0)
    verification_rate: Mapped[float] = mapped_column(default=0)
    repeat_damage_rate: Mapped[float] = mapped_column(default=0)

    user: Mapped["User | None"] = relationship(back_populates="contractor")
    work_orders: Mapped[list["WorkOrder"]] = relationship(back_populates="contractor")
    assets: Mapped[list["Asset"]] = relationship(back_populates="contractor")


class Asset(Base):
    __tablename__ = "assets"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    asset_code: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    type: Mapped[str] = mapped_column(String(50))
    name: Mapped[str] = mapped_column(String(250))
    location: Mapped[str | None] = mapped_column(String(250), nullable=True)
    geom = mapped_column(Geography(geometry_type="POINT", srid=4326, spatial_index=True), nullable=False)
    district: Mapped[str | None] = mapped_column(String(100), nullable=True)
    construction_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    length_km: Mapped[float | None] = mapped_column(nullable=True)
    project_cost: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    health_score: Mapped[float | None] = mapped_column(nullable=True)
    risk_score: Mapped[float | None] = mapped_column(nullable=True)
    status: Mapped[str | None] = mapped_column(String(80), nullable=True)
    last_inspection: Mapped[date | None] = mapped_column(Date, nullable=True)
    contractor_id: Mapped[str | None] = mapped_column(ForeignKey("contractors.id"), nullable=True)

    contractor: Mapped["Contractor | None"] = relationship(back_populates="assets")
    complaints: Mapped[list["Complaint"]] = relationship(back_populates="asset")
    detections: Mapped[list["AIDetection"]] = relationship(back_populates="asset")
    risk_scores: Mapped[list["RiskScore"]] = relationship(back_populates="asset")
    work_orders: Mapped[list["WorkOrder"]] = relationship(back_populates="asset")
    maintenance: Mapped[list["MaintenanceHistory"]] = relationship(back_populates="asset")
    alerts: Mapped[list["Alert"]] = relationship(back_populates="asset")
    satellite: Mapped["SatelliteRecord | None"] = relationship(back_populates="asset", uselist=False)


class Complaint(Base):
    __tablename__ = "complaints"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    asset_id: Mapped[str] = mapped_column(ForeignKey("assets.id"), index=True)
    citizen_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    issue_type: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(Text)
    geom = mapped_column(Geography(geometry_type="POINT", srid=4326, spatial_index=True), nullable=False)
    image_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_status: Mapped[str] = mapped_column(String(30), default="Pending")
    risk_score: Mapped[float | None] = mapped_column(nullable=True)
    status: Mapped[str] = mapped_column(String(80), default="Reported", index=True)
    work_order_id: Mapped[str | None] = mapped_column(ForeignKey("work_orders.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    asset: Mapped["Asset"] = relationship(back_populates="complaints")
    citizen: Mapped["User"] = relationship(back_populates="complaints", foreign_keys=[citizen_id])
    work_order: Mapped["WorkOrder | None"] = relationship(
        foreign_keys=[work_order_id]
    )
    detections: Mapped[list["AIDetection"]] = relationship(back_populates="complaint")


class AIDetection(Base):
    __tablename__ = "ai_detections"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    asset_id: Mapped[str] = mapped_column(ForeignKey("assets.id"), index=True)
    complaint_id: Mapped[str | None] = mapped_column(ForeignKey("complaints.id"), nullable=True)
    image_url: Mapped[str] = mapped_column(Text)
    detection_type: Mapped[str] = mapped_column(String(100))
    confidence: Mapped[float] = mapped_column()
    severity: Mapped[str] = mapped_column(String(40))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    asset: Mapped["Asset"] = relationship(back_populates="detections")
    complaint: Mapped["Complaint | None"] = relationship(back_populates="detections")


class RiskScore(Base):
    __tablename__ = "risk_scores"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    asset_id: Mapped[str] = mapped_column(ForeignKey("assets.id"), index=True)
    score: Mapped[float] = mapped_column()
    level: Mapped[str] = mapped_column(String(30))
    factors: Mapped[dict] = mapped_column(JSONB, default=dict)
    calculated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    asset: Mapped["Asset"] = relationship(back_populates="risk_scores")


class WorkOrder(Base):
    __tablename__ = "work_orders"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    asset_id: Mapped[str] = mapped_column(ForeignKey("assets.id"), index=True)
    complaint_id: Mapped[str | None] = mapped_column(ForeignKey("complaints.id"), nullable=True, unique=True)
    contractor_id: Mapped[str | None] = mapped_column(ForeignKey("contractors.id"), index=True, nullable=True)
    issue: Mapped[str] = mapped_column(String(250))
    required_action: Mapped[str] = mapped_column(String(500))
    priority: Mapped[str] = mapped_column(String(40), default="Moderate", index=True)
    status: Mapped[str] = mapped_column(String(50), default="Pending", index=True)
    risk_score: Mapped[float | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    deadline: Mapped[date | None] = mapped_column(Date, nullable=True)
    before_image: Mapped[str | None] = mapped_column(Text, nullable=True)
    after_image: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    verification_status: Mapped[str] = mapped_column(String(40), default="Not started")
    verification_confidence: Mapped[float | None] = mapped_column(nullable=True)

    asset: Mapped["Asset"] = relationship(back_populates="work_orders")
    contractor: Mapped["Contractor | None"] = relationship(back_populates="work_orders")
    complaint: Mapped["Complaint | None"] = relationship(
        foreign_keys=[complaint_id]
    )


class MaintenanceHistory(Base):
    __tablename__ = "maintenance_history"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    asset_id: Mapped[str] = mapped_column(ForeignKey("assets.id"), index=True)
    date: Mapped[date] = mapped_column(Date)
    type: Mapped[str] = mapped_column(String(100))
    detail: Mapped[str] = mapped_column(Text)

    asset: Mapped["Asset"] = relationship(back_populates="maintenance")


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    asset_id: Mapped[str] = mapped_column(ForeignKey("assets.id"), index=True)
    work_order_id: Mapped[str | None] = mapped_column(ForeignKey("work_orders.id"), nullable=True)
    level: Mapped[str] = mapped_column(String(30))
    risk_score: Mapped[float] = mapped_column()
    issue: Mapped[str] = mapped_column(String(250))
    ai_confidence: Mapped[float | None] = mapped_column(nullable=True)
    recommended_action: Mapped[str] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    resolved: Mapped[bool] = mapped_column(Boolean, default=False, index=True)

    asset: Mapped["Asset"] = relationship(back_populates="alerts")


class SatelliteRecord(Base):
    __tablename__ = "satellite_records"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    asset_id: Mapped[str] = mapped_column(ForeignKey("assets.id"), unique=True)
    development_status: Mapped[str | None] = mapped_column(String(250), nullable=True)
    change_detection: Mapped[str | None] = mapped_column(String(50), nullable=True)
    environmental_risk: Mapped[str | None] = mapped_column(String(50), nullable=True)
    last_observation: Mapped[date | None] = mapped_column(Date, nullable=True)

    asset: Mapped["Asset"] = relationship(back_populates="satellite")
    observations: Mapped[list["SatelliteObservation"]] = relationship(
        back_populates="satellite_record", cascade="all, delete-orphan"
    )


class SatelliteObservation(Base):
    __tablename__ = "satellite_observations"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    satellite_record_id: Mapped[str] = mapped_column(ForeignKey("satellite_records.id"), index=True)
    year: Mapped[str] = mapped_column(String(10))
    label: Mapped[str] = mapped_column(String(150))
    note: Mapped[str] = mapped_column(Text)

    satellite_record: Mapped["SatelliteRecord"] = relationship(back_populates="observations")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
    asset_id: Mapped[str | None] = mapped_column(ForeignKey("assets.id"), nullable=True)
    actor_type: Mapped[str] = mapped_column(String(50))
    actor_id: Mapped[str] = mapped_column(String(100))
    event_type: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(Text)
    system_decision: Mapped[str | None] = mapped_column(Text, nullable=True)
    log_metadata: Mapped[dict] = mapped_column(JSONB, default=dict)


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    title: Mapped[str] = mapped_column(String(250))
    body: Mapped[str] = mapped_column(Text)
    read: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="notifications")


class Upload(Base):
    __tablename__ = "uploads"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    url: Mapped[str] = mapped_column(Text)
    mime: Mapped[str] = mapped_column(String(100))
    size: Mapped[int] = mapped_column(Integer)
    uploaded_by: Mapped[str] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
