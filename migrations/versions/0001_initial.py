"""initial InfraSetu schema"""

from alembic import op
import sqlalchemy as sa
from geoalchemy2 import Geography
from sqlalchemy.dialects.postgresql import JSONB

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")

    op.create_table(
        "users",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("name", sa.String(150), nullable=False),
        sa.Column("role", sa.String(30), nullable=False),
        sa.Column("organisation", sa.String(200)),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_users_role", "users", ["role"])

    op.create_table(
        "contractors",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("user_id", sa.String(64), sa.ForeignKey("users.id"), unique=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("license_status", sa.String(40), nullable=False),
        sa.Column("district", sa.String(100)),
        sa.Column("active_orders", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("completed_orders", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("average_completion_days", sa.Float(), nullable=False, server_default="0"),
        sa.Column("performance_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("verification_rate", sa.Float(), nullable=False, server_default="0"),
        sa.Column("repeat_damage_rate", sa.Float(), nullable=False, server_default="0"),
    )

    op.create_table(
        "assets",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("asset_code", sa.String(100), unique=True, nullable=False),
        sa.Column("type", sa.String(50), nullable=False),
        sa.Column("name", sa.String(250), nullable=False),
        sa.Column("location", sa.String(250)),
        sa.Column("geom", Geography(geometry_type="POINT", srid=4326), nullable=False),
        sa.Column("district", sa.String(100)),
        sa.Column("construction_year", sa.Integer()),
        sa.Column("length_km", sa.Float()),
        sa.Column("project_cost", sa.Numeric(14, 2)),
        sa.Column("health_score", sa.Float()),
        sa.Column("risk_score", sa.Float()),
        sa.Column("status", sa.String(80)),
        sa.Column("last_inspection", sa.Date()),
        sa.Column("contractor_id", sa.String(64), sa.ForeignKey("contractors.id")),
    )
    op.create_index("ix_assets_asset_code", "assets", ["asset_code"])

    op.create_table(
        "work_orders",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("asset_id", sa.String(64), sa.ForeignKey("assets.id"), nullable=False),
        sa.Column("complaint_id", sa.String(64), unique=True),
        sa.Column("contractor_id", sa.String(64), sa.ForeignKey("contractors.id")),
        sa.Column("issue", sa.String(250), nullable=False),
        sa.Column("required_action", sa.String(500), nullable=False),
        sa.Column("priority", sa.String(40), nullable=False),
        sa.Column("status", sa.String(50), nullable=False),
        sa.Column("risk_score", sa.Float()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deadline", sa.Date()),
        sa.Column("before_image", sa.Text()),
        sa.Column("after_image", sa.Text()),
        sa.Column("notes", sa.Text()),
        sa.Column("verification_status", sa.String(40), nullable=False),
        sa.Column("verification_confidence", sa.Float()),
    )
    op.create_index("ix_work_orders_asset_id", "work_orders", ["asset_id"])
    op.create_index("ix_work_orders_contractor_id", "work_orders", ["contractor_id"])
    op.create_index("ix_work_orders_status", "work_orders", ["status"])
    op.create_index("ix_work_orders_priority", "work_orders", ["priority"])

    op.create_table(
        "complaints",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("asset_id", sa.String(64), sa.ForeignKey("assets.id"), nullable=False),
        sa.Column("citizen_id", sa.String(64), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("issue_type", sa.String(100), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("geom", Geography(geometry_type="POINT", srid=4326), nullable=False),
        sa.Column("image_url", sa.Text()),
        sa.Column("ai_status", sa.String(30), nullable=False),
        sa.Column("risk_score", sa.Float()),
        sa.Column("status", sa.String(80), nullable=False),
        sa.Column("work_order_id", sa.String(64)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_complaints_asset_id", "complaints", ["asset_id"])
    op.create_index("ix_complaints_citizen_id", "complaints", ["citizen_id"])
    op.create_index("ix_complaints_status", "complaints", ["status"])

    op.create_foreign_key(
        "fk_work_orders_complaint",
        "work_orders", "complaints", ["complaint_id"], ["id"]
    )
    op.create_foreign_key(
        "fk_complaints_work_order",
        "complaints", "work_orders", ["work_order_id"], ["id"]
    )

    op.create_table(
        "ai_detections",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("asset_id", sa.String(64), sa.ForeignKey("assets.id"), nullable=False),
        sa.Column("complaint_id", sa.String(64), sa.ForeignKey("complaints.id")),
        sa.Column("image_url", sa.Text(), nullable=False),
        sa.Column("detection_type", sa.String(100), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("severity", sa.String(40), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_ai_detections_asset_id", "ai_detections", ["asset_id"])

    op.create_table(
        "risk_scores",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("asset_id", sa.String(64), sa.ForeignKey("assets.id"), nullable=False),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column("level", sa.String(30), nullable=False),
        sa.Column("factors", JSONB, nullable=False),
        sa.Column("calculated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_risk_scores_asset_id", "risk_scores", ["asset_id"])

    op.create_table(
        "maintenance_history",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("asset_id", sa.String(64), sa.ForeignKey("assets.id"), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("type", sa.String(100), nullable=False),
        sa.Column("detail", sa.Text(), nullable=False),
    )
    op.create_index("ix_maintenance_history_asset_id", "maintenance_history", ["asset_id"])

    op.create_table(
        "alerts",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("asset_id", sa.String(64), sa.ForeignKey("assets.id"), nullable=False),
        sa.Column("work_order_id", sa.String(64)),
        sa.Column("level", sa.String(30), nullable=False),
        sa.Column("risk_score", sa.Float(), nullable=False),
        sa.Column("issue", sa.String(250), nullable=False),
        sa.Column("ai_confidence", sa.Float()),
        sa.Column("recommended_action", sa.String(500), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("resolved", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.create_index("ix_alerts_asset_id", "alerts", ["asset_id"])
    op.create_index("ix_alerts_resolved", "alerts", ["resolved"])

    op.create_table(
        "satellite_records",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("asset_id", sa.String(64), sa.ForeignKey("assets.id"), unique=True, nullable=False),
        sa.Column("development_status", sa.String(250)),
        sa.Column("change_detection", sa.String(50)),
        sa.Column("environmental_risk", sa.String(50)),
        sa.Column("last_observation", sa.Date()),
    )
    op.create_table(
        "satellite_observations",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("satellite_record_id", sa.String(64), sa.ForeignKey("satellite_records.id"), nullable=False),
        sa.Column("year", sa.String(10), nullable=False),
        sa.Column("label", sa.String(150), nullable=False),
        sa.Column("note", sa.Text(), nullable=False),
    )
    op.create_index("ix_satellite_observations_record", "satellite_observations", ["satellite_record_id"])

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("timestamp", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("asset_id", sa.String(64), sa.ForeignKey("assets.id")),
        sa.Column("actor_type", sa.String(50), nullable=False),
        sa.Column("actor_id", sa.String(100), nullable=False),
        sa.Column("event_type", sa.String(100), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("system_decision", sa.Text()),
        sa.Column("metadata", JSONB, nullable=False),
    )
    op.create_index("ix_audit_logs_timestamp", "audit_logs", ["timestamp"])

    op.create_table(
        "notifications",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("user_id", sa.String(64), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("title", sa.String(250), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("read", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_notifications_user_id", "notifications", ["user_id"])

    op.create_table(
        "uploads",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("url", sa.Text(), nullable=False),
        sa.Column("mime", sa.String(100), nullable=False),
        sa.Column("size", sa.Integer(), nullable=False),
        sa.Column("uploaded_by", sa.String(64), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.execute("CREATE INDEX ix_assets_geom_gist ON assets USING GIST (geom)")
    op.execute("CREATE INDEX ix_complaints_geom_gist ON complaints USING GIST (geom)")
    op.execute("CREATE INDEX ix_alerts_resolved_risk ON alerts (resolved, risk_score DESC)")


def downgrade() -> None:
    for table in [
        "uploads", "notifications", "audit_logs", "satellite_observations",
        "satellite_records", "alerts", "maintenance_history", "risk_scores",
        "ai_detections", "complaints", "work_orders", "assets", "contractors", "users",
    ]:
        op.drop_table(table)
