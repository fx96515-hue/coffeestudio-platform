"""Embedding service for semantic search using OpenAI embeddings.

This service generates embeddings for entities (Cooperatives, Roasters) using
OpenAI's text-embedding-3-small model (1536 dimensions).
"""

from __future__ import annotations

import structlog
from typing import Union

import httpx

from app.core.config import settings
from app.models.cooperative import Cooperative
from app.models.roaster import Roaster

log = structlog.get_logger()


class EmbeddingService:
    """Service for generating embeddings using OpenAI API.

    Features:
    - Generates embeddings from text using OpenAI text-embedding-3-small
    - Graceful degradation when API key is not available
    - Batch processing support
    - Entity-specific embedding generation
    """

    def __init__(self) -> None:
        self.api_key = settings.OPENAI_API_KEY
        self.model = settings.EMBEDDING_MODEL
        self.base_url = "https://api.openai.com/v1/embeddings"
        self.timeout = 30.0

    def is_available(self) -> bool:
        """Check if the embedding service is available (API key configured)."""
        return self.api_key is not None and len(self.api_key.strip()) > 0

    async def generate_embedding(self, text: str) -> list[float] | None:
        """Generate embedding for a single text.

        Args:
            text: Text to embed

        Returns:
            List of floats (1536 dimensions) or None if service unavailable
        """
        if not self.is_available():
            log.warning("embedding_service_unavailable", reason="no_api_key")
            return None

        if not text or not text.strip():
            log.warning("embedding_empty_text")
            return None

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.base_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self.model,
                        "input": text,
                    },
                    timeout=self.timeout,
                )
                response.raise_for_status()
                data = response.json()
                embedding = data["data"][0]["embedding"]
                log.info(
                    "embedding_generated",
                    text_length=len(text),
                    embedding_dim=len(embedding),
                )
                return embedding
        except httpx.HTTPStatusError as e:
            log.error(
                "openai_api_error",
                status_code=e.response.status_code,
                error=str(e),
            )
            return None
        except Exception as e:
            log.error("embedding_generation_failed", error=str(e))
            return None

    async def generate_embeddings_batch(
        self, texts: list[str]
    ) -> list[list[float] | None]:
        """Generate embeddings for multiple texts in batch.

        Args:
            texts: List of texts to embed

        Returns:
            List of embeddings (or None for failed items)
        """
        if not self.is_available():
            log.warning("embedding_service_unavailable", reason="no_api_key")
            return [None] * len(texts)

        # Filter out empty texts
        valid_texts = [(i, t) for i, t in enumerate(texts) if t and t.strip()]
        if not valid_texts:
            log.warning("embedding_batch_all_empty")
            return [None] * len(texts)

        try:
            # OpenAI supports batch embeddings
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.base_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self.model,
                        "input": [t for _, t in valid_texts],
                    },
                    timeout=self.timeout * 2,  # Double timeout for batch
                )
                response.raise_for_status()
                data = response.json()

                # Map embeddings back to original positions
                results: list[list[float] | None] = [None] * len(texts)
                for (orig_idx, _), emb_data in zip(valid_texts, data["data"]):
                    results[orig_idx] = emb_data["embedding"]

                log.info(
                    "embeddings_batch_generated",
                    total=len(texts),
                    successful=sum(1 for r in results if r is not None),
                )
                return results
        except Exception as e:
            log.error("batch_embedding_failed", error=str(e))
            return [None] * len(texts)

    def generate_entity_text(self, entity: Union[Cooperative, Roaster]) -> str:
        """Generate text representation of an entity for embedding.

        Combines relevant fields into a single text that captures the entity's
        characteristics for semantic search.

        Args:
            entity: Cooperative or Roaster instance

        Returns:
            Combined text representation
        """
        parts = []

        # Always include name
        parts.append(f"Name: {entity.name}")

        # Type-specific fields
        if isinstance(entity, Cooperative):
            if entity.region:
                parts.append(f"Region: {entity.region}")
            if entity.certifications:
                parts.append(f"Certifications: {entity.certifications}")
            if entity.varieties:
                parts.append(f"Varieties: {entity.varieties}")
            if entity.altitude_m:
                parts.append(f"Altitude: {entity.altitude_m}m")
            if entity.notes:
                # Truncate notes to avoid token limits
                notes_preview = entity.notes[:500]
                parts.append(f"Notes: {notes_preview}")
        elif isinstance(entity, Roaster):
            if entity.city:
                parts.append(f"City: {entity.city}")
            if entity.peru_focus:
                parts.append("Focus: Peru specialty coffee")
            if entity.specialty_focus:
                parts.append("Focus: Specialty coffee")
            if entity.price_position:
                parts.append(f"Price position: {entity.price_position}")
            if entity.notes:
                # Truncate notes to avoid token limits
                notes_preview = entity.notes[:500]
                parts.append(f"Notes: {notes_preview}")

        # Join all parts
        text = " | ".join(parts)
        return text

    async def generate_entity_embedding(
        self, entity: Union[Cooperative, Roaster]
    ) -> list[float] | None:
        """Generate embedding for an entity.

        Args:
            entity: Cooperative or Roaster instance

        Returns:
            Embedding vector or None if generation failed
        """
        text = self.generate_entity_text(entity)
        return await self.generate_embedding(text)
