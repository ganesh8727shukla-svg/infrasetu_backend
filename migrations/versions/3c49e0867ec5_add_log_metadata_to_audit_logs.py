"""add log metadata to audit logs"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "3c49e0867ec5"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "audit_logs",
        "metadata",
        new_column_name="log_metadata",
        existing_type=postgresql.JSONB(astext_type=sa.Text()),
        existing_nullable=False,
    )

    op.drop_index(
        "ix_satellite_observations_record",
        table_name="satellite_observations",
    )

    op.create_index(
        "ix_satellite_observations_satellite_record_id",
        "satellite_observations",
        ["satellite_record_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_satellite_observations_satellite_record_id",
        table_name="satellite_observations",
    )

    op.create_index(
        "ix_satellite_observations_record",
        "satellite_observations",
        ["satellite_record_id"],
        unique=False,
    )

    op.alter_column(
        "audit_logs",
        "log_metadata",
        new_column_name="metadata",
        existing_type=postgresql.JSONB(astext_type=sa.Text()),
        existing_nullable=False,
    )
