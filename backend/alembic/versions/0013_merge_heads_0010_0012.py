"""merge heads 0010 + 0012

Revision ID: 0013_merge_heads_0010_0012
Revises: 0010_peru_sourcing_intelligence_v0_4_0, 0012_peru_sourcing_intelligence_v0_4_0
Create Date: 2025-12-31
"""
from __future__ import annotations

from alembic import op  # noqa: F401
import sqlalchemy as sa  # noqa: F401

revision = "0013_merge_heads_0010_0012"
down_revision = ("0010_peru_sourcing_intelligence_v0_4_0", "0012_peru_sourcing_intelligence_v0_4_0")
branch_labels = None
depends_on = None

def upgrade() -> None:
    pass

def downgrade() -> None:
    pass