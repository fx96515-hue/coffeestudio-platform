"""peru_sourcing_intelligence_v0_4_0

Revision ID: 0012_peru_sourcing_intelligence_v0_4_0
Revises: 0011_add_shipments_table
Create Date: 2025-12-30 16:38:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "0012_peru_sourcing_intelligence_v0_4_0"
down_revision = "0011_add_shipments_table"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    # Create regions table
    if not insp.has_table("regions"):
        op.create_table("regions",
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=128), nullable=False),
        sa.Column('country', sa.String(length=64), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('elevation_min_m', sa.Float(), nullable=True),
        sa.Column('elevation_max_m', sa.Float(), nullable=True),
        sa.Column('avg_temperature_c', sa.Float(), nullable=True),
        sa.Column('rainfall_mm', sa.Float(), nullable=True),
        sa.Column('humidity_pct', sa.Float(), nullable=True),
        sa.Column('soil_type', sa.String(length=128), nullable=True),
        sa.Column('production_volume_kg', sa.Float(), nullable=True),
        sa.Column('production_share_pct', sa.Float(), nullable=True),
        sa.Column('harvest_months', sa.String(length=64), nullable=True),
        sa.Column('typical_varieties', sa.String(length=255), nullable=True),
        sa.Column('typical_processing', sa.String(length=128), nullable=True),
        sa.Column('quality_profile', sa.Text(), nullable=True),
        sa.Column('main_port', sa.String(length=64), nullable=True),
        sa.Column('transport_time_hours', sa.Float(), nullable=True),
        sa.Column('logistics_cost_per_kg', sa.Float(), nullable=True),
        sa.Column('infrastructure_score', sa.Float(), nullable=True),
        sa.Column('weather_risk', sa.String(length=32), nullable=True),
        sa.Column('political_risk', sa.String(length=32), nullable=True),
        sa.Column('logistics_risk', sa.String(length=32), nullable=True),
        sa.Column('quality_consistency_score', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name', 'country', name='uq_region_name_country')
    )
    op.create_index(op.f('ix_regions_name'), 'regions', ['name'], unique=False)
    op.create_index(op.f('ix_regions_country'), 'regions', ['country'], unique=False)

    # Extend cooperatives table with new JSONB fields
    op.add_column('cooperatives', sa.Column('operational_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('cooperatives', sa.Column('export_readiness', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('cooperatives', sa.Column('financial_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('cooperatives', sa.Column('social_impact_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('cooperatives', sa.Column('digital_footprint', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('cooperatives', sa.Column('sourcing_scores', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('cooperatives', sa.Column('communication_metrics', postgresql.JSONB(astext_type=sa.Text()), nullable=True))


def downgrade() -> None:
    # Remove columns from cooperatives
    op.drop_column('cooperatives', 'communication_metrics')
    op.drop_column('cooperatives', 'sourcing_scores')
    op.drop_column('cooperatives', 'digital_footprint')
    op.drop_column('cooperatives', 'social_impact_data')
    op.drop_column('cooperatives', 'financial_data')
    op.drop_column('cooperatives', 'export_readiness')
    op.drop_column('cooperatives', 'operational_data')
    
    # Drop regions table
    op.drop_index(op.f('ix_regions_country'), table_name='regions')
    op.drop_index(op.f('ix_regions_name'), table_name='regions')
    op.drop_table('regions')

