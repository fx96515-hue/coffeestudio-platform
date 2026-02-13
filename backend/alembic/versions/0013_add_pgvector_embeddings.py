"""Add pgvector extension and embedding columns

Revision ID: 0013_add_pgvector_embeddings
Revises: 0012_add_quality_alerts_table
Create Date: 2026-02-12

NOTE: This migration gracefully skips pgvector setup in environments where the
extension is not available (e.g., CI). In such cases, embedding columns and
semantic search features will not be available, but the rest of the application
will continue to function normally.

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.exc import ProgrammingError


revision = "0013_add_pgvector_embeddings"
down_revision = "0012_add_quality_alerts_table"
branch_labels = None
depends_on = None


def upgrade():
    # Try to enable pgvector extension - gracefully skip if not available (e.g., CI)
    # This allows the migration to succeed in test/CI environments without pgvector
    conn = op.get_bind()
    try:
        conn.execute(sa.text("CREATE EXTENSION IF NOT EXISTS vector"))
    except ProgrammingError as e:
        import warnings

        warnings.warn(
            f"pgvector extension not available - skipping vector columns. "
            f"Semantic search features will be unavailable. Error: {e}"
        )
        return

    # Add embedding column to cooperatives table
    op.execute(
        """
        ALTER TABLE cooperatives 
        ADD COLUMN IF NOT EXISTS embedding vector(1536)
        """
    )

    # Add embedding column to roasters table
    op.execute(
        """
        ALTER TABLE roasters 
        ADD COLUMN IF NOT EXISTS embedding vector(1536)
        """
    )

    # Create HNSW index for cooperatives embeddings (cosine distance)
    # HNSW is better for high-dimensional vectors than IVFFlat
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_cooperatives_embedding_cosine 
        ON cooperatives 
        USING hnsw (embedding vector_cosine_ops)
        """
    )

    # Create HNSW index for roasters embeddings (cosine distance)
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_roasters_embedding_cosine 
        ON roasters 
        USING hnsw (embedding vector_cosine_ops)
        """
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
