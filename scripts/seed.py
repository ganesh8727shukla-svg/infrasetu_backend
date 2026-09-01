from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal
from pathlib import Path
import sys

from sqlalchemy import create_engine, delete, text
from sqlalchemy.orm import sessionmaker
from geoalchemy2 import WKTElement

ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.core.config import settings
from app.core.security import hash_password
from app.models import (
    User,
    Contractor,
    Asset,
    Complaint,
    WorkOrder,
    AIDetection,
    RiskScore,
    MaintenanceHistory,
    Alert,
    SatelliteRecord,
    SatelliteObservation,
    AuditLog,
    Notification,
)

DATABASE_URL = settings.database_url

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


def utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def dt_from_iso(value: str) -> datetime:
    return utc(datetime.fromisoformat(value.replace("Z", "+00:00")))


def point(latitude: float, longitude: float) -> WKTElement:
    return WKTElement(
        f"POINT({longitude} {latitude})",
        srid=4326,
    )


def crore(value: str) -> Decimal:
    cleaned = (
        value.replace("₹", "")
        .replace("Cr", "")
        .strip()
    )
    return Decimal(cleaned)


def log(message: str) -> None:
    print(f"[seed] {message}")


USERS = [
    {
        "id": "GOV-ADMIN",
        "name": "InfraSetu Administrator",
        "role": "admin",
        "organisation": "InfraSetu Government Administration",
        "password_hash": hash_password("demo1234"),
    },
    {
        "id": "USR-8821",
        "name": "R. Deshmukh",
        "role": "citizen",
        "organisation": "Citizen",
        "password_hash": hash_password("demo1234"),
    },
    {
        "id": "USR-7710",
        "name": "S. Kulkarni",
        "role": "citizen",
        "organisation": "Citizen",
        "password_hash": hash_password("demo1234"),
    },
    {
        "id": "USR-4412",
        "name": "A. Pawar",
        "role": "citizen",
        "organisation": "Citizen",
        "password_hash": hash_password("demo1234"),
    },
    {
        "id": "USR-9902",
        "name": "M. Shaikh",
        "role": "citizen",
        "organisation": "Citizen",
        "password_hash": hash_password("demo1234"),
    },
    {
        "id": "USR-3310",
        "name": "P. Nair",
        "role": "citizen",
        "organisation": "Citizen",
        "password_hash": hash_password("demo1234"),
    },
    {
        "id": "USR-1180",
        "name": "K. Jadhav",
        "role": "citizen",
        "organisation": "Citizen",
        "password_hash": hash_password("demo1234"),
    },
    {
        "id": "CON-01-USER",
        "name": "Apex Infrastructure",
        "role": "contractor",
        "organisation": "Apex Infrastructure",
        "password_hash": hash_password("demo1234"),
    },
    {
        "id": "CON-02-USER",
        "name": "Maharashtra RoadWorks",
        "role": "contractor",
        "organisation": "Maharashtra RoadWorks",
        "password_hash": hash_password("demo1234"),
    },
    {
        "id": "CON-03-USER",
        "name": "UrbanLink Projects",
        "role": "contractor",
        "organisation": "UrbanLink Projects",
        "password_hash": hash_password("demo1234"),
    },
    {
        "id": "CON-04-USER",
        "name": "Shivam Infra Solutions",
        "role": "contractor",
        "organisation": "Shivam Infra Solutions",
        "password_hash": hash_password("demo1234"),
    },
]


CONTRACTORS = [
    {
        "id": "CON-01",
        "user_id": "CON-01-USER",
        "name": "Apex Infrastructure",
        "license_status": "ACTIVE",
        "district": "Mumbai",
        "active_orders": 4,
        "completed_orders": 83,
        "average_completion_days": 2.4,
        "performance_score": 91,
        "verification_rate": 94,
        "repeat_damage_rate": 8,
    },
    {
        "id": "CON-02",
        "user_id": "CON-02-USER",
        "name": "Maharashtra RoadWorks",
        "license_status": "ACTIVE",
        "district": "Pune",
        "active_orders": 6,
        "completed_orders": 142,
        "average_completion_days": 3.1,
        "performance_score": 84,
        "verification_rate": 88,
        "repeat_damage_rate": 12,
    },
    {
        "id": "CON-03",
        "user_id": "CON-03-USER",
        "name": "UrbanLink Projects",
        "license_status": "UNDER REVIEW",
        "district": "Thane",
        "active_orders": 2,
        "completed_orders": 57,
        "average_completion_days": 4.6,
        "performance_score": 68,
        "verification_rate": 74,
        "repeat_damage_rate": 21,
    },
    {
        "id": "CON-04",
        "user_id": "CON-04-USER",
        "name": "Shivam Infra Solutions",
        "license_status": "ACTIVE",
        "district": "Nashik",
        "active_orders": 3,
        "completed_orders": 96,
        "average_completion_days": 2.9,
        "performance_score": 79,
        "verification_rate": 82,
        "repeat_damage_rate": 14,
    },
]


ASSETS = [
    {
        "id": "ROAD-MH-001",
        "asset_code": "ROAD-MH-001",
        "type": "Road",
        "name": "Eastern Corridor Link Road",
        "location": "Mumbai, Maharashtra",
        "latitude": 19.076,
        "longitude": 72.8777,
        "district": "Mumbai",
        "construction_year": 2023,
        "length_km": 4.2,
        "project_cost": "₹8.4 Cr",
        "health_score": 42,
        "risk_score": 87,
        "status": "Repair Active",
        "contractor_id": "CON-01",
        "last_inspection": "2026-08-13",
    },
    {
        "id": "ROAD-MH-002",
        "asset_code": "ROAD-MH-002",
        "type": "Road",
        "name": "Ghodbunder Service Road",
        "location": "Thane, Maharashtra",
        "latitude": 19.2183,
        "longitude": 72.9781,
        "district": "Thane",
        "construction_year": 2021,
        "length_km": 6.8,
        "project_cost": "₹11.2 Cr",
        "health_score": 88,
        "risk_score": 21,
        "status": "Operational",
        "contractor_id": "CON-03",
        "last_inspection": "2026-08-07",
    },
    {
        "id": "ROAD-MH-003",
        "asset_code": "ROAD-MH-003",
        "type": "Road",
        "name": "Kharadi Bypass Stretch",
        "location": "Pune, Maharashtra",
        "latitude": 18.5514,
        "longitude": 73.9412,
        "district": "Pune",
        "construction_year": 2019,
        "length_km": 9.4,
        "project_cost": "₹18.9 Cr",
        "health_score": 58,
        "risk_score": 66,
        "status": "Under Observation",
        "contractor_id": "CON-02",
        "last_inspection": "2026-08-16",
    },
    {
        "id": "BRIDGE-MH-014",
        "asset_code": "BRIDGE-MH-014",
        "type": "Bridge",
        "name": "Godavari Crossing Bridge",
        "location": "Nashik, Maharashtra",
        "latitude": 19.9975,
        "longitude": 73.7898,
        "district": "Nashik",
        "construction_year": 2015,
        "length_km": 1.1,
        "project_cost": "₹34.6 Cr",
        "health_score": 39,
        "risk_score": 91,
        "status": "Exception Review",
        "contractor_id": "CON-04",
        "last_inspection": "2026-08-18",
    },
    {
        "id": "FLYOVER-MH-007",
        "asset_code": "FLYOVER-MH-007",
        "type": "Flyover",
        "name": "Sion Junction Flyover",
        "location": "Mumbai, Maharashtra",
        "latitude": 19.0433,
        "longitude": 72.8622,
        "district": "Mumbai",
        "construction_year": 2018,
        "length_km": 2.3,
        "project_cost": "₹52.1 Cr",
        "health_score": 74,
        "risk_score": 44,
        "status": "Under Observation",
        "contractor_id": "CON-01",
        "last_inspection": "2026-08-10",
    },
    {
        "id": "ROAD-MH-032",
        "asset_code": "ROAD-MH-032",
        "type": "Road",
        "name": "Panvel Industrial Approach",
        "location": "Raigad, Maharashtra",
        "latitude": 18.9894,
        "longitude": 73.1175,
        "district": "Raigad",
        "construction_year": 2022,
        "length_km": 5.5,
        "project_cost": "₹9.7 Cr",
        "health_score": 51,
        "risk_score": 78,
        "status": "Awaiting Verification",
        "contractor_id": "CON-02",
        "last_inspection": "2026-08-17",
    },
    {
        "id": "TUNNEL-MH-003",
        "asset_code": "TUNNEL-MH-003",
        "type": "Tunnel",
        "name": "Khandala Ghat Tunnel",
        "location": "Pune, Maharashtra",
        "latitude": 18.7557,
        "longitude": 73.3873,
        "district": "Pune",
        "construction_year": 2020,
        "length_km": 1.8,
        "project_cost": "₹78.3 Cr",
        "health_score": 81,
        "risk_score": 29,
        "status": "Operational",
        "contractor_id": "CON-02",
        "last_inspection": "2026-07-29",
    },
    {
        "id": "CULVERT-MH-021",
        "asset_code": "CULVERT-MH-021",
        "type": "Culvert",
        "name": "Vasai Drainage Culvert",
        "location": "Palghar, Maharashtra",
        "latitude": 19.391,
        "longitude": 72.8397,
        "district": "Palghar",
        "construction_year": 2017,
        "length_km": 0.3,
        "project_cost": "₹2.1 Cr",
        "health_score": 63,
        "risk_score": 52,
        "status": "Under Observation",
        "contractor_id": "CON-04",
        "last_inspection": "2026-08-04",
    },
    {
        "id": "ROAD-MH-045",
        "asset_code": "ROAD-MH-045",
        "type": "Road",
        "name": "Aurangabad Ring Segment",
        "location": "Chhatrapati Sambhajinagar",
        "latitude": 19.8762,
        "longitude": 75.3433,
        "district": "Sambhajinagar",
        "construction_year": 2024,
        "length_km": 7.2,
        "project_cost": "₹14.5 Cr",
        "health_score": 92,
        "risk_score": 14,
        "status": "Operational",
        "contractor_id": "CON-04",
        "last_inspection": "2026-07-20",
    },
    {
        "id": "BRIDGE-MH-021",
        "asset_code": "BRIDGE-MH-021",
        "type": "Bridge",
        "name": "Ulhas River Bridge",
        "location": "Thane, Maharashtra",
        "latitude": 19.2403,
        "longitude": 73.1305,
        "district": "Thane",
        "construction_year": 2012,
        "length_km": 0.9,
        "project_cost": "₹27.8 Cr",
        "health_score": 44,
        "risk_score": 84,
        "status": "Repair Active",
        "contractor_id": "CON-03",
        "last_inspection": "2026-08-15",
    },
]


DETECTIONS = [
    {
        "id": "AID-5001",
        "asset_id": "ROAD-MH-001",
        "detection_type": "Pothole",
        "confidence": 94,
        "severity": "critical",
        "created_at": "2026-08-19T10:28:00+05:30",
    },
    {
        "id": "AID-5002",
        "asset_id": "ROAD-MH-001",
        "detection_type": "Crack",
        "confidence": 81,
        "severity": "high",
        "created_at": "2026-08-19T06:40:00+05:30",
    },
    {
        "id": "AID-5003",
        "asset_id": "ROAD-MH-001",
        "detection_type": "Waterlogging",
        "confidence": 42,
        "severity": "moderate",
        "created_at": "2026-08-18T11:20:00+05:30",
    },
    {
        "id": "AID-5004",
        "asset_id": "BRIDGE-MH-021",
        "detection_type": "Structural concern",
        "confidence": 89,
        "severity": "critical",
        "created_at": "2026-08-19T10:08:00+05:30",
    },
    {
        "id": "AID-5005",
        "asset_id": "ROAD-MH-032",
        "detection_type": "Waterlogging",
        "confidence": 77,
        "severity": "high",
        "created_at": "2026-08-19T09:40:00+05:30",
    },
    {
        "id": "AID-5006",
        "asset_id": "ROAD-MH-003",
        "detection_type": "Surface deterioration",
        "confidence": 68,
        "severity": "high",
        "created_at": "2026-08-19T00:40:00+05:30",
    },
]


COMPLAINTS = [
    {
        "id": "CIT-10291",
        "asset_id": "ROAD-MH-001",
        "citizen_id": "USR-8821",
        "latitude": 19.076,
        "longitude": 72.8777,
        "issue_type": "Pothole",
        "description": "Deep pothole near the service lane merge, two-wheelers skidding.",
        "ai_status": "Completed",
        "risk_score": 87,
        "status": "Work Order Created",
        "created_at": "2026-08-19T09:55:00+05:30",
        "work_order_id": "WO-1024",
    },
    {
        "id": "CIT-10288",
        "asset_id": "ROAD-MH-032",
        "citizen_id": "USR-7710",
        "latitude": 18.9894,
        "longitude": 73.1175,
        "issue_type": "Waterlogging",
        "description": "Water stagnates for hours after rain near the industrial gate.",
        "ai_status": "Completed",
        "risk_score": 78,
        "status": "Work Order Created",
        "created_at": "2026-08-19T07:40:00+05:30",
        "work_order_id": "WO-1026",
    },
    {
        "id": "CIT-10284",
        "asset_id": "ROAD-MH-003",
        "citizen_id": "USR-4412",
        "latitude": 18.5514,
        "longitude": 73.9412,
        "issue_type": "Crack",
        "description": "Longitudinal cracking visible across both lanes.",
        "ai_status": "Completed",
        "risk_score": 66,
        "status": "Risk Assigned",
        "created_at": "2026-08-18T10:40:00+05:30",
        "work_order_id": None,
    },
    {
        "id": "CIT-10279",
        "asset_id": "BRIDGE-MH-021",
        "citizen_id": "USR-9902",
        "latitude": 19.2403,
        "longitude": 73.1305,
        "issue_type": "Damaged barrier",
        "description": "Side barrier damaged after a collision, debris on footpath.",
        "ai_status": "Completed",
        "risk_score": 84,
        "status": "AI Analysed",
        "created_at": "2026-08-17T10:40:00+05:30",
        "work_order_id": None,
    },
    {
        "id": "CIT-10270",
        "asset_id": "ROAD-MH-002",
        "citizen_id": "USR-3310",
        "latitude": 19.2183,
        "longitude": 72.9781,
        "issue_type": "Road surface damage",
        "description": "Loose gravel near the bus stop.",
        "ai_status": "Completed",
        "risk_score": 28,
        "status": "Resolved",
        "created_at": "2026-08-10T10:40:00+05:30",
        "work_order_id": None,
    },
    {
        "id": "CIT-10265",
        "asset_id": "ROAD-MH-045",
        "citizen_id": "USR-1180",
        "latitude": 19.8762,
        "longitude": 75.3433,
        "issue_type": "Other",
        "description": "Street lighting outage reported alongside the carriageway.",
        "ai_status": "Completed",
        "risk_score": 12,
        "status": "Rejected",
        "created_at": "2026-08-05T10:40:00+05:30",
        "work_order_id": None,
    },
]


WORK_ORDERS = [
    {
        "id": "WO-1024",
        "asset_id": "ROAD-MH-001",
        "complaint_id": "CIT-10291",
        "contractor_id": "CON-01",
        "issue": "Pothole",
        "required_action": "Road surface repair",
        "priority": "Critical",
        "status": "In Progress",
        "risk_score": 87,
        "created_at": "2026-08-19T10:00:00+05:30",
        "deadline": "2026-08-20",
        "verification_status": "Not started",
    },
    {
        "id": "WO-1025",
        "asset_id": "BRIDGE-MH-021",
        "complaint_id": None,
        "contractor_id": "CON-03",
        "issue": "Structural concern",
        "required_action": "Structural assessment and bearing repair",
        "priority": "Critical",
        "status": "Exception Review",
        "risk_score": 91,
        "created_at": "2026-08-19T10:10:00+05:30",
        "deadline": "2026-08-21",
        "verification_status": "Not started",
    },
    {
        "id": "WO-1026",
        "asset_id": "ROAD-MH-032",
        "complaint_id": "CIT-10288",
        "contractor_id": "CON-02",
        "issue": "Waterlogging",
        "required_action": "Drainage clearing and camber correction",
        "priority": "High",
        "status": "Verification",
        "risk_score": 78,
        "created_at": "2026-08-17T10:40:00+05:30",
        "deadline": "2026-08-18",
        "verification_status": "Analysing",
    },
    {
        "id": "WO-1021",
        "asset_id": "ROAD-MH-003",
        "complaint_id": None,
        "contractor_id": "CON-02",
        "issue": "Surface deterioration",
        "required_action": "Patch resurfacing",
        "priority": "High",
        "status": "Assigned",
        "risk_score": 66,
        "created_at": "2026-08-16T10:40:00+05:30",
        "deadline": "2026-08-16",
        "verification_status": "Not started",
    },
    {
        "id": "WO-1018",
        "asset_id": "FLYOVER-MH-007",
        "complaint_id": None,
        "contractor_id": "CON-01",
        "issue": "Expansion joint wear",
        "required_action": "Joint sealing",
        "priority": "Normal",
        "status": "Completed",
        "risk_score": 44,
        "created_at": "2026-08-10T10:40:00+05:30",
        "deadline": "2026-08-23",
        "verification_status": "Verified",
        "verification_confidence": 93,
    },
    {
        "id": "WO-1015",
        "asset_id": "CULVERT-MH-021",
        "complaint_id": None,
        "contractor_id": "CON-04",
        "issue": "Silt accumulation",
        "required_action": "Desilting",
        "priority": "Normal",
        "status": "Pending",
        "risk_score": 52,
        "created_at": "2026-08-15T10:40:00+05:30",
        "deadline": "2026-08-14",
        "verification_status": "Not started",
    },
    {
        "id": "WO-1011",
        "asset_id": "ROAD-MH-002",
        "complaint_id": None,
        "contractor_id": "CON-03",
        "issue": "Loose gravel",
        "required_action": "Surface dressing",
        "priority": "Normal",
        "status": "Completed",
        "risk_score": 28,
        "created_at": "2026-08-07T10:40:00+05:30",
        "deadline": "2026-08-27",
        "verification_status": "Verified",
        "verification_confidence": 88,
    },
]


ALERTS = [
    {
        "id": "ALR-9001",
        "asset_id": "ROAD-MH-001",
        "work_order_id": "WO-1024",
        "level": "critical",
        "risk_score": 87,
        "issue": "Pothole detected",
        "ai_confidence": 94,
        "recommended_action": "Urgent maintenance",
        "created_at": "2026-08-19T10:28:00+05:30",
        "resolved": False,
    },
    {
        "id": "ALR-9002",
        "asset_id": "BRIDGE-MH-021",
        "work_order_id": "WO-1025",
        "level": "critical",
        "risk_score": 91,
        "issue": "Structural concern",
        "ai_confidence": 89,
        "recommended_action": "Exception requiring authorized review",
        "created_at": "2026-08-19T10:08:00+05:30",
        "resolved": False,
    },
    {
        "id": "ALR-9003",
        "asset_id": "ROAD-MH-032",
        "work_order_id": "WO-1026",
        "level": "high",
        "risk_score": 78,
        "issue": "Waterlogging",
        "ai_confidence": 77,
        "recommended_action": "Schedule drainage inspection",
        "created_at": "2026-08-19T09:40:00+05:30",
        "resolved": False,
    },
    {
        "id": "ALR-9004",
        "asset_id": "ROAD-MH-003",
        "work_order_id": None,
        "level": "high",
        "risk_score": 66,
        "issue": "Surface deterioration",
        "ai_confidence": 68,
        "recommended_action": "Routine resurfacing",
        "created_at": "2026-08-19T00:40:00+05:30",
        "resolved": False,
    },
    {
        "id": "ALR-9005",
        "asset_id": "CULVERT-MH-021",
        "work_order_id": None,
        "level": "moderate",
        "risk_score": 52,
        "issue": "Silt accumulation",
        "ai_confidence": 61,
        "recommended_action": "Pre-monsoon cleaning",
        "created_at": "2026-08-17T10:40:00+05:30",
        "resolved": False,
    },
    {
        "id": "ALR-9006",
        "asset_id": "FLYOVER-MH-007",
        "work_order_id": "WO-1018",
        "level": "moderate",
        "risk_score": 44,
        "issue": "Expansion joint wear",
        "ai_confidence": 58,
        "recommended_action": "Monitor next cycle",
        "created_at": "2026-08-14T10:40:00+05:30",
        "resolved": True,
    },
]


RISK_SCORES = [
    {
        "id": "RISK-ROAD-MH-001",
        "asset_id": "ROAD-MH-001",
        "score": 87,
        "level": "critical",
        "factors": [
            {"label": "AI severity", "value": "91"},
            {"label": "Traffic", "value": "High"},
            {"label": "Asset age", "value": "3 years"},
        ],
        "calculated_at": "2026-08-19T10:37:00+05:30",
    },
    {
        "id": "RISK-BRIDGE-MH-021",
        "asset_id": "BRIDGE-MH-021",
        "score": 84,
        "level": "critical",
        "factors": [
            {"label": "Structural concern", "value": "Critical"},
            {"label": "Asset age", "value": "14 years"},
            {"label": "AI confidence", "value": "89%"},
        ],
        "calculated_at": "2026-08-19T10:08:00+05:30",
    },
    {
        "id": "RISK-ROAD-MH-032",
        "asset_id": "ROAD-MH-032",
        "score": 78,
        "level": "high",
        "factors": [
            {"label": "Waterlogging", "value": "High"},
            {"label": "AI confidence", "value": "77%"},
            {"label": "Environmental risk", "value": "Moderate"},
        ],
        "calculated_at": "2026-08-19T09:40:00+05:30",
    },
    {
        "id": "RISK-ROAD-MH-003",
        "asset_id": "ROAD-MH-003",
        "score": 66,
        "level": "high",
        "factors": [
            {"label": "Surface deterioration", "value": "High"},
            {"label": "AI confidence", "value": "68%"},
            {"label": "Asset age", "value": "7 years"},
        ],
        "calculated_at": "2026-08-19T00:40:00+05:30",
    },
    {
        "id": "RISK-FLYOVER-MH-007",
        "asset_id": "FLYOVER-MH-007",
        "score": 44,
        "level": "moderate",
        "factors": [
            {"label": "Expansion joint wear", "value": "Moderate"},
        ],
        "calculated_at": "2026-08-14T10:40:00+05:30",
    },
    {
        "id": "RISK-CULVERT-MH-021",
        "asset_id": "CULVERT-MH-021",
        "score": 52,
        "level": "moderate",
        "factors": [
            {"label": "Silt accumulation", "value": "Moderate"},
        ],
        "calculated_at": "2026-08-17T10:40:00+05:30",
    },
]


MAINTENANCE = [
    {
        "id": "MHIST-001",
        "asset_id": "ROAD-MH-001",
        "date": "2026-04-21",
        "type": "Inspection",
        "detail": "Routine annual inspection — no major defect.",
    },
    {
        "id": "MHIST-002",
        "asset_id": "ROAD-MH-001",
        "date": "2026-06-05",
        "type": "Repair",
        "detail": "Patch repair over 40 m stretch.",
    },
    {
        "id": "MHIST-003",
        "asset_id": "ROAD-MH-001",
        "date": "2026-07-20",
        "type": "Inspection",
        "detail": "Post-monsoon condition survey.",
    },
    {
        "id": "MHIST-004",
        "asset_id": "ROAD-MH-001",
        "date": "2026-08-18",
        "type": "New damage",
        "detail": "Pothole formation detected from citizen evidence.",
    },
]


def build_satellite_records():
    records = []
    observations = []

    for asset in ASSETS:
        risk = asset["risk_score"]

        development_status = (
            "Completed"
            if asset["construction_year"] >= 2023
            else "Operational"
        )

        if risk > 70:
            change = "High"
        elif risk > 40:
            change = "Moderate"
        else:
            change = "Low"

        if asset["district"] == "Mumbai":
            environmental = "High"
        elif risk > 60:
            environmental = "Moderate"
        else:
            environmental = "Low"

        record_id = f"SAT-{asset['id']}"

        records.append(
            {
                "id": record_id,
                "asset_id": asset["id"],
                "development_status": development_status,
                "change_detection": change,
                "environmental_risk": environmental,
                "last_observation": "2026-08-19",
            }
        )

        timeline = [
            (
                "2022",
                "Existing road",
                "Baseline surface observed in reference imagery.",
            ),
            (
                "2023",
                "Construction detected",
                "Earthworks and alignment change identified.",
            ),
            (
                "2024",
                "Road completed",
                "Continuous paved surface confirmed.",
            ),
            (
                "2025",
                "Surrounding development",
                "Land-use change detected within 500 m buffer.",
            ),
            (
                "2026",
                "Current observation",
                "Moderate surface change; monsoon drainage stress.",
            ),
        ]

        for index, (year, label, note) in enumerate(timeline, start=1):
            observations.append(
                {
                    "id": f"{record_id}-OBS-{index}",
                    "satellite_record_id": record_id,
                    "year": year,
                    "label": label,
                    "note": note,
                }
            )

    return records, observations


AUDIT_LOGS = [
    {
        "id": "A10231",
        "timestamp": "2026-08-19T09:53:00+05:30",
        "asset_id": "ROAD-MH-001",
        "actor_type": "CITIZEN",
        "actor_id": "USR-8821",
        "event_type": "Citizen Report Received",
        "description": "Citizen report CIT-10291 received with image evidence.",
        "system_decision": "CIT-10291",
        "metadata": {
            "inputs": [
                {"label": "Issue type", "value": "Pothole"},
                {"label": "Geo-tag", "value": "19.0760, 72.8777"},
            ],
            "outputs": [
                {"label": "Complaint", "value": "CIT-10291"},
            ],
            "policy": "INTAKE_V1",
            "action": "Queued for AI analysis",
        },
    },
    {
        "id": "A10232",
        "timestamp": "2026-08-19T09:55:00+05:30",
        "asset_id": "ROAD-MH-001",
        "actor_type": "AUTOMATED SYSTEM",
        "actor_id": "vision-engine",
        "event_type": "AI Analysed",
        "description": "Computer vision detection completed on submitted evidence.",
        "system_decision": "Pothole • 94% confidence",
        "metadata": {
            "inputs": [
                {"label": "Evidence images", "value": "1"},
            ],
            "outputs": [
                {"label": "Detection", "value": "Pothole"},
                {"label": "Confidence", "value": "94%"},
                {"label": "AI severity", "value": "91"},
            ],
            "policy": "VISION_DETECT_V4",
            "action": "Forwarded to risk engine",
        },
    },
    {
        "id": "A10233",
        "timestamp": "2026-08-19T09:57:00+05:30",
        "asset_id": "ROAD-MH-001",
        "actor_type": "AUTOMATED SYSTEM",
        "actor_id": "risk-engine",
        "event_type": "Risk Calculated",
        "description": "Rule-based risk assessment executed for ROAD-MH-001.",
        "system_decision": "Risk = 87",
        "metadata": {
            "inputs": [
                {"label": "AI severity", "value": "91"},
                {"label": "Traffic", "value": "High"},
                {"label": "Asset age", "value": "3 years"},
            ],
            "outputs": [
                {"label": "Risk", "value": "87"},
                {"label": "Level", "value": "CRITICAL"},
            ],
            "policy": "CRITICAL_RISK_V2",
            "action": "Urgent Work Order Created",
        },
    },
    {
        "id": "A10234",
        "timestamp": "2026-08-19T10:00:00+05:30",
        "asset_id": "ROAD-MH-001",
        "actor_type": "AUTOMATED SYSTEM",
        "actor_id": "workflow-engine",
        "event_type": "Work Order Created",
        "description": "System-generated work order for urgent maintenance.",
        "system_decision": "WO-1024",
        "metadata": {
            "policy": "AUTO_WORKORDER_V3",
            "action": "Contractor assignment triggered",
            "outputs": [
                {"label": "Work order", "value": "WO-1024"},
            ],
        },
    },
    {
        "id": "A10235",
        "timestamp": "2026-08-19T10:01:00+05:30",
        "asset_id": "ROAD-MH-001",
        "actor_type": "SYSTEM",
        "actor_id": "assignment-engine",
        "event_type": "Contractor Assigned",
        "description": "Contractor selected by performance and jurisdiction rules.",
        "system_decision": "Apex Infrastructure",
        "metadata": {
            "inputs": [
                {"label": "District", "value": "Mumbai"},
                {"label": "Performance score", "value": "91"},
            ],
            "policy": "ASSIGNMENT_RULE_V2",
            "action": "Work order dispatched",
        },
    },
    {
        "id": "A10236",
        "timestamp": "2026-08-19T10:10:00+05:30",
        "asset_id": "BRIDGE-MH-021",
        "actor_type": "AUTOMATED SYSTEM",
        "actor_id": "risk-engine",
        "event_type": "Exception Raised",
        "description": "Structural risk above automation threshold.",
        "system_decision": "Exception requiring authorized review",
        "metadata": {
            "policy": "STRUCTURAL_EXCEPTION_V1",
            "action": "Routed to authorized engineer",
        },
    },
    {
        "id": "A10237",
        "timestamp": "2026-08-15T10:40:00+05:30",
        "asset_id": "FLYOVER-MH-007",
        "actor_type": "AUTOMATED SYSTEM",
        "actor_id": "vision-engine",
        "event_type": "Repair Verified",
        "description": "Before/after evidence comparison completed.",
        "system_decision": "Verified • 93%",
        "metadata": {
            "policy": "REPAIR_VERIFY_V2",
            "action": "Work order WO-1018 completed",
        },
    },
]


NOTIFICATIONS = [
    {
        "id": "N1",
        "user_id": "GOV-ADMIN",
        "title": "Critical infrastructure detected",
        "body": "Road MH-001",
        "read": False,
        "created_at": "2026-08-19T10:28:00+05:30",
    },
    {
        "id": "N2",
        "user_id": "GOV-ADMIN",
        "title": "Work order approaching deadline",
        "body": "WO-1024",
        "read": False,
        "created_at": "2026-08-19T09:10:00+05:30",
    },
    {
        "id": "N3",
        "user_id": "GOV-ADMIN",
        "title": "Repair verified",
        "body": "WO-1018",
        "read": True,
        "created_at": "2026-08-15T10:40:00+05:30",
    },
    {
        "id": "N4",
        "user_id": "GOV-ADMIN",
        "title": "Satellite observation updated",
        "body": "Road MH-004",
        "read": False,
        "created_at": "2026-08-18T10:40:00+05:30",
    },
]


def seed() -> None:
    session = SessionLocal()

    try:
        log("Starting database seed...")
        log("Clearing existing development data...")

        session.execute(delete(Notification))
        session.execute(delete(AuditLog))
        session.execute(delete(SatelliteObservation))
        session.execute(delete(SatelliteRecord))
        session.execute(delete(Alert))
        session.execute(delete(MaintenanceHistory))
        session.execute(delete(RiskScore))
        session.execute(delete(AIDetection))

        session.execute(
            text(
                """
                UPDATE complaints
                SET work_order_id = NULL
                """
            )
        )

        session.execute(delete(WorkOrder))
        session.execute(delete(Complaint))
        session.execute(delete(Asset))
        session.execute(delete(Contractor))

        session.execute(text("DELETE FROM uploads"))

        session.execute(delete(User))

        session.flush()

        log(f"Inserting {len(USERS)} users...")

        for row in USERS:
            session.add(User(**row))

        session.flush()

        log(f"Inserting {len(CONTRACTORS)} contractors...")

        for row in CONTRACTORS:
            session.add(Contractor(**row))

        session.flush()

        log(f"Inserting {len(ASSETS)} assets...")

        for row in ASSETS:
            session.add(
                Asset(
                    id=row["id"],
                    asset_code=row["asset_code"],
                    type=row["type"],
                    name=row["name"],
                    location=row["location"],
                    geom=point(
                        row["latitude"],
                        row["longitude"],
                    ),
                    district=row["district"],
                    construction_year=row["construction_year"],
                    length_km=row["length_km"],
                    project_cost=crore(row["project_cost"]),
                    health_score=row["health_score"],
                    risk_score=row["risk_score"],
                    status=row["status"],
                    last_inspection=date.fromisoformat(
                        row["last_inspection"]
                    ),
                    contractor_id=row["contractor_id"],
                )
            )

        session.flush()

        log(f"Inserting {len(COMPLAINTS)} complaints...")

        for row in COMPLAINTS:
            session.add(
                Complaint(
                    id=row["id"],
                    asset_id=row["asset_id"],
                    citizen_id=row["citizen_id"],
                    issue_type=row["issue_type"],
                    description=row["description"],
                    geom=point(
                        row["latitude"],
                        row["longitude"],
                    ),
                    image_url=None,
                    ai_status=row["ai_status"],
                    risk_score=row["risk_score"],
                    status=row["status"],
                    work_order_id=None,
                    created_at=dt_from_iso(row["created_at"]),
                )
            )

        session.flush()

        log(f"Inserting {len(WORK_ORDERS)} work orders...")

        for row in WORK_ORDERS:
            session.add(
                WorkOrder(
                    id=row["id"],
                    asset_id=row["asset_id"],
                    complaint_id=row["complaint_id"],
                    contractor_id=row["contractor_id"],
                    issue=row["issue"],
                    required_action=row["required_action"],
                    priority=row["priority"],
                    status=row["status"],
                    risk_score=row["risk_score"],
                    created_at=dt_from_iso(row["created_at"]),
                    deadline=date.fromisoformat(row["deadline"]),
                    before_image=None,
                    after_image=None,
                    notes=None,
                    verification_status=row["verification_status"],
                    verification_confidence=row.get(
                        "verification_confidence"
                    ),
                )
            )

        session.flush()

        log("Restoring complaint/work-order relationships...")

        for row in COMPLAINTS:
            if row["work_order_id"]:
                session.execute(
                    text(
                        """
                        UPDATE complaints
                        SET work_order_id = :work_order_id
                        WHERE id = :complaint_id
                        """
                    ),
                    {
                        "work_order_id": row["work_order_id"],
                        "complaint_id": row["id"],
                    },
                )

        session.flush()

        log(f"Inserting {len(DETECTIONS)} AI detections...")

        for row in DETECTIONS:
            session.add(
                AIDetection(
                    id=row["id"],
                    asset_id=row["asset_id"],
                    complaint_id=None,
                    image_url="",
                    detection_type=row["detection_type"],
                    confidence=row["confidence"],
                    severity=row["severity"],
                    created_at=dt_from_iso(row["created_at"]),
                )
            )

        session.flush()

        log(f"Inserting {len(RISK_SCORES)} risk scores...")

        for row in RISK_SCORES:
            session.add(
                RiskScore(
                    id=row["id"],
                    asset_id=row["asset_id"],
                    score=row["score"],
                    level=row["level"],
                    factors=row["factors"],
                    calculated_at=dt_from_iso(row["calculated_at"]),
                )
            )

        session.flush()

        log(f"Inserting {len(ALERTS)} alerts...")

        for row in ALERTS:
            session.add(
                Alert(
                    id=row["id"],
                    asset_id=row["asset_id"],
                    work_order_id=row["work_order_id"],
                    level=row["level"],
                    risk_score=row["risk_score"],
                    issue=row["issue"],
                    ai_confidence=row["ai_confidence"],
                    recommended_action=row["recommended_action"],
                    created_at=dt_from_iso(row["created_at"]),
                    resolved=row["resolved"],
                )
            )

        session.flush()

        log(f"Inserting {len(MAINTENANCE)} maintenance records...")

        for row in MAINTENANCE:
            session.add(
                MaintenanceHistory(
                    id=row["id"],
                    asset_id=row["asset_id"],
                    date=date.fromisoformat(row["date"]),
                    type=row["type"],
                    detail=row["detail"],
                )
            )

        session.flush()

        satellite_records, satellite_observations = build_satellite_records()

        log(f"Inserting {len(satellite_records)} satellite records...")

        for row in satellite_records:
            session.add(SatelliteRecord(**row))

        session.flush()

        log(
            f"Inserting {len(satellite_observations)} satellite observations..."
        )

        for row in satellite_observations:
            session.add(SatelliteObservation(**row))

        session.flush()

        log(f"Inserting {len(AUDIT_LOGS)} audit logs...")

        for row in AUDIT_LOGS:
            session.add(
                AuditLog(
                    id=row["id"],
                    timestamp=dt_from_iso(row["timestamp"]),
                    asset_id=row["asset_id"],
                    actor_type=row["actor_type"],
                    actor_id=row["actor_id"],
                    event_type=row["event_type"],
                    description=row["description"],
                    system_decision=row["system_decision"],
                    log_metadata=row["metadata"],
                )
            )

        session.flush()

        log(f"Inserting {len(NOTIFICATIONS)} notifications...")

        for row in NOTIFICATIONS:
            session.add(
                Notification(
                    id=row["id"],
                    user_id=row["user_id"],
                    title=row["title"],
                    body=row["body"],
                    read=row["read"],
                    created_at=dt_from_iso(row["created_at"]),
                )
            )

        session.flush()

        session.commit()

        log("========================================")
        log("DATABASE SEED COMPLETED SUCCESSFULLY")
        log("========================================")
        log(f"Users:                 {len(USERS)}")
        log(f"Contractors:           {len(CONTRACTORS)}")
        log(f"Assets:                {len(ASSETS)}")
        log(f"Complaints:            {len(COMPLAINTS)}")
        log(f"Work orders:           {len(WORK_ORDERS)}")
        log(f"AI detections:         {len(DETECTIONS)}")
        log(f"Risk scores:           {len(RISK_SCORES)}")
        log(f"Alerts:                {len(ALERTS)}")
        log(f"Maintenance records:   {len(MAINTENANCE)}")
        log(f"Satellite records:     {len(satellite_records)}")
        log(f"Satellite observations:{len(satellite_observations)}")
        log(f"Audit logs:            {len(AUDIT_LOGS)}")
        log(f"Notifications:         {len(NOTIFICATIONS)}")

    except Exception:
        session.rollback()
        log("SEED FAILED — transaction rolled back.")
        raise

    finally:
        session.close()


if __name__ == "__main__":
    seed()