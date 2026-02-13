"""Add pgvector extension and embedding columns

Revision ID: 0013_add_pgvector_embeddings
Revises: 0012_add_quality_alerts_table
Create Date: 2026-02-12

"""

from alembic import op


revision = "0013_add_pgvector_embeddings"
down_revision = "0012_add_quality_alerts_table"
branch_labels = None
depends_on = None


def upgrade():
    # Try to enable pgvector - skip gracefully if not available (CI environment)
    try:
        op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    except Exception:
        import warnings

        warnings.warn(
            "pgvector extension not available - skipping vector columns and indexes"
        )
        return

    # Add embedding columns and indexes only if extension is available
    op.execute(
        """ALTER TABLE cooperatives ADD COLUMN IF NOT EXISTS embedding vector(1536)"""
    )
    op.execute(
        """ALTER TABLE roasters ADD COLUMN IF NOT EXISTS embedding vector(1536)"""
    )
    op.execute(
        """CREATE INDEX IF NOT EXISTS ix_cooperatives_embedding_cosine ON cooperatives USING hnsw (embedding vector_cosine_ops)"""
    )
    op.execute(
        """CREATE INDEX IF NOT EXISTS ix_roasters_embedding_cosine ON roasters USING hnsw (embedding vector_cosine_ops)"""
    )


def downgrade():
    # Drop indexes first
    op.execute("DROP INDEX IF EXISTS ix_roasters_embedding_cosine")
    op.execute("DROP INDEX IF EXISTS ix_cooperatives_embedding_cosine")

    # Drop columns
    op.execute("ALTER TABLE roasters DROP COLUMN IF EXISTS embedding")
    op.execute("ALTER TABLE cooperatives DROP COLUMN IF EXISTS embedding")

    # Note: We don't drop the vector extension as it might be used by other tables
    # If you really need to drop it, uncomment the next line:
    # op.execute("DROP EXTENSION IF EXISTS vector")
