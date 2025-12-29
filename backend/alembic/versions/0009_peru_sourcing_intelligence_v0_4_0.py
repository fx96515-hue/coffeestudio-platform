"""Peru sourcing intelligence system

Revision ID: 0009_peru_sourcing_intelligence_v0_4_0
Revises: 0008_timestamp_defaults_kb_cupping_v0_3_2b
Create Date: 2025-12-29
"""

from alembic import op
import sqlalchemy as sa


revision = "0009_peru_sourcing_intelligence_v0_4_0"
down_revision = "0008_timestamp_defaults_kb_cupping_v0_3_2b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create regions table
    op.create_table(
        "regions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("country", sa.String(length=100), nullable=False, server_default="Peru"),
        sa.Column("polygon", sa.JSON(), nullable=True),
        sa.Column("elevation_range", sa.JSON(), nullable=True),
        sa.Column("climate_data", sa.JSON(), nullable=True),
        sa.Column("soil_type", sa.String(length=100), nullable=True),
        sa.Column("growing_conditions_score", sa.Float(), nullable=True),
        sa.Column("production_data", sa.JSON(), nullable=True),
        sa.Column("economic_data", sa.JSON(), nullable=True),
        sa.Column("quality_profile", sa.JSON(), nullable=True),
        sa.Column("infrastructure_data", sa.JSON(), nullable=True),
        sa.Column("harvest_season", sa.String(length=100), nullable=True),
        sa.Column("cooperatives_count", sa.Integer(), nullable=True),
        sa.Column("certifications_pct", sa.JSON(), nullable=True),
        sa.Column("risk_factors", sa.JSON(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "last_updated",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index("ix_regions_name", "regions", ["name"], unique=True)
    op.create_index("ix_regions_country", "regions", ["country"], unique=False)

    # Extend cooperatives table with new JSONB fields
    op.add_column("cooperatives", sa.Column("operational_data", sa.JSON(), nullable=True))
    op.add_column("cooperatives", sa.Column("export_readiness", sa.JSON(), nullable=True))
    op.add_column("cooperatives", sa.Column("financial_data", sa.JSON(), nullable=True))
    op.add_column("cooperatives", sa.Column("social_impact_data", sa.JSON(), nullable=True))
    op.add_column("cooperatives", sa.Column("digital_footprint", sa.JSON(), nullable=True))
    op.add_column("cooperatives", sa.Column("sourcing_scores", sa.JSON(), nullable=True))
    op.add_column("cooperatives", sa.Column("communication_metrics", sa.JSON(), nullable=True))


def downgrade() -> None:
    # Remove columns from cooperatives
    op.drop_column("cooperatives", "communication_metrics")
    op.drop_column("cooperatives", "sourcing_scores")
    op.drop_column("cooperatives", "digital_footprint")
    op.drop_column("cooperatives", "social_impact_data")
    op.drop_column("cooperatives", "financial_data")
    op.drop_column("cooperatives", "export_readiness")
    op.drop_column("cooperatives", "operational_data")

    # Drop regions table
    op.drop_index("ix_regions_country", "regions")
    op.drop_index("ix_regions_name", "regions")
    op.drop_table("regions")
