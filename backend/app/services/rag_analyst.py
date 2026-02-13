"""RAG-based AI analyst service for coffee sourcing intelligence.

This service uses Retrieval-Augmented Generation (RAG) to answer questions
about cooperatives, roasters, market data, and sourcing using the existing
pgvector semantic search infrastructure.
"""

from __future__ import annotations

import structlog
from sqlalchemy import text
from sqlalchemy.orm import Session

import httpx

from app.core.config import settings
from app.schemas.rag_analyst import RAGResponse, RAGSource, ConversationMessage
from app.services.embedding import EmbeddingService

log = structlog.get_logger()


class RAGAnalystService:
    """RAG-based AI analyst for coffee sourcing intelligence."""

    def __init__(self) -> None:
        self.api_key = settings.OPENAI_API_KEY
        self.model = settings.RAG_LLM_MODEL
        self.temperature = settings.RAG_TEMPERATURE
        self.max_context_entities = settings.RAG_MAX_CONTEXT_ENTITIES
        self.max_history = settings.RAG_MAX_CONVERSATION_HISTORY
        self.base_url = "https://api.openai.com/v1/chat/completions"
        self.timeout = 60.0
        self.embedding_service = EmbeddingService()

    def is_available(self) -> bool:
        """Check if RAG service is available (API key configured)."""
        return self.api_key is not None and len(self.api_key.strip()) > 0

    async def ask(
        self,
        question: str,
        conversation_history: list[ConversationMessage],
        db: Session,
    ) -> RAGResponse:
        """Answer a question using RAG.

        Args:
            question: User's question
            conversation_history: Previous conversation messages
            db: Database session

        Returns:
            RAG response with answer and sources

        Raises:
            Exception: If service unavailable or API call fails
        """
        if not self.is_available():
            log.warning("rag_service_unavailable", reason="no_api_key")
            raise Exception("RAG service not available: API key not configured")

        # Retrieve relevant context
        context = await self._retrieve_context(question, db)
        log.info(
            "rag_context_retrieved",
            question_length=len(question),
            context_entities=len(context),
        )

        # Build system prompt with context
        system_prompt = self._build_system_prompt(context)

        # Build messages for API
        messages = [{"role": "system", "content": system_prompt}]

        # Add conversation history (limited)
        for msg in conversation_history[-self.max_history :]:
            messages.append({"role": msg.role, "content": msg.content})

        # Add current question
        messages.append({"role": "user", "content": question})

        # Call OpenAI Chat Completion API
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
                        "messages": messages,
                        "temperature": self.temperature,
                    },
                    timeout=self.timeout,
                )
                response.raise_for_status()
                data = response.json()

                answer = data["choices"][0]["message"]["content"]
                tokens_used = data.get("usage", {}).get("total_tokens")

                log.info(
                    "rag_answer_generated",
                    question_length=len(question),
                    answer_length=len(answer),
                    tokens_used=tokens_used,
                )

                # Build sources from context
                sources = [
                    RAGSource(
                        entity_type=ctx["entity_type"],
                        entity_id=ctx["entity_id"],
                        name=ctx["name"],
                        similarity_score=ctx["similarity_score"],
                    )
                    for ctx in context
                ]

                return RAGResponse(
                    answer=answer,
                    sources=sources,
                    model=self.model,
                    tokens_used=tokens_used,
                )

        except httpx.HTTPStatusError as e:
            log.error(
                "openai_api_error",
                status_code=e.response.status_code,
                error=str(e),
            )
            raise Exception(f"OpenAI API error: {e.response.status_code}")
        except Exception as e:
            log.error("rag_answer_generation_failed", error=str(e))
            raise

    async def _retrieve_context(self, question: str, db: Session) -> list[dict]:
        """Retrieve relevant context entities using pgvector similarity search.

        Args:
            question: User's question
            db: Database session

        Returns:
            List of context entities with metadata
        """
        # Generate embedding for question
        query_embedding = await self.embedding_service.generate_embedding(question)
        if not query_embedding:
            log.warning("rag_context_retrieval_failed", reason="embedding_failed")
            return []

        # Search cooperatives
        coop_query = text(
            """
            SELECT 
                'cooperative' as entity_type,
                id, 
                name, 
                region, 
                certifications,
                altitude_m,
                varieties,
                1 - (embedding <=> :query_embedding) AS similarity
            FROM cooperatives
            WHERE embedding IS NOT NULL
            ORDER BY embedding <=> :query_embedding
            LIMIT :limit
            """
        )

        coop_rows = db.execute(
            coop_query,
            {
                "query_embedding": query_embedding,
                "limit": self.max_context_entities // 2,
            },
        ).fetchall()

        # Search roasters
        roaster_query = text(
            """
            SELECT 
                'roaster' as entity_type,
                id, 
                name, 
                city,
                peru_focus,
                specialty_focus,
                price_position,
                1 - (embedding <=> :query_embedding) AS similarity
            FROM roasters
            WHERE embedding IS NOT NULL
            ORDER BY embedding <=> :query_embedding
            LIMIT :limit
            """
        )

        roaster_rows = db.execute(
            roaster_query,
            {
                "query_embedding": query_embedding,
                "limit": self.max_context_entities // 2,
            },
        ).fetchall()

        # Combine and format results
        context = []

        for row in coop_rows:
            context.append(
                {
                    "entity_type": row[0],
                    "entity_id": row[1],
                    "name": row[2],
                    "region": row[3],
                    "certifications": row[4],
                    "altitude_m": row[5],
                    "varieties": row[6],
                    "similarity_score": max(0.0, min(1.0, row[7])),
                }
            )

        for row in roaster_rows:
            context.append(
                {
                    "entity_type": row[0],
                    "entity_id": row[1],
                    "name": row[2],
                    "city": row[3],
                    "peru_focus": row[4],
                    "specialty_focus": row[5],
                    "price_position": row[6],
                    "similarity_score": max(0.0, min(1.0, row[7])),
                }
            )

        # Sort by similarity and limit total
        context.sort(key=lambda x: x["similarity_score"], reverse=True)
        return context[: self.max_context_entities]

    def _build_system_prompt(self, context: list[dict]) -> str:
        """Build system prompt with retrieved context.

        Args:
            context: List of context entities

        Returns:
            System prompt string
        """
        base_prompt = """Du bist ein KI-Assistent für Kaffee-Sourcing und Spezialitätenkaffee-Handel.
Du hilfst dabei, Informationen über Kooperativen, Röstereien, Marktdaten und Sourcing-Möglichkeiten zu finden und zu analysieren.

Du sprichst primär Deutsch, kannst aber auch auf Englisch antworten wenn gewünscht.

WICHTIGE RICHTLINIEN:
- Beantworte Fragen präzise und auf Basis der bereitgestellten Daten
- Nenne IMMER die Quellen (Namen und IDs der Entities) in deiner Antwort
- Wenn Daten fehlen oder unvollständig sind, sage das klar
- Gib keine Informationen an, die nicht in den Quelldaten vorhanden sind
- Sei hilfsbereit und professionell
"""

        if not context:
            base_prompt += "\nAktuell sind keine spezifischen Daten verfügbar. Antworte allgemein basierend auf Kaffee-Sourcing-Wissen."
            return base_prompt

        base_prompt += "\n\n=== VERFÜGBARE DATEN ===\n"

        # Add cooperatives
        coops = [c for c in context if c["entity_type"] == "cooperative"]
        if coops:
            base_prompt += "\n## Kooperativen:\n"
            for coop in coops:
                base_prompt += f"\n**{coop['name']}** (ID: {coop['entity_id']})\n"
                if coop.get("region"):
                    base_prompt += f"- Region: {coop['region']}\n"
                if coop.get("certifications"):
                    base_prompt += f"- Zertifizierungen: {coop['certifications']}\n"
                if coop.get("varieties"):
                    base_prompt += f"- Sorten: {coop['varieties']}\n"
                if coop.get("altitude_m"):
                    base_prompt += f"- Höhe: {coop['altitude_m']}m\n"

        # Add roasters
        roasters = [r for r in context if r["entity_type"] == "roaster"]
        if roasters:
            base_prompt += "\n## Röstereien:\n"
            for roaster in roasters:
                base_prompt += f"\n**{roaster['name']}** (ID: {roaster['entity_id']})\n"
                if roaster.get("city"):
                    base_prompt += f"- Stadt: {roaster['city']}\n"
                if roaster.get("peru_focus"):
                    base_prompt += "- Peru-Fokus: Ja\n"
                if roaster.get("specialty_focus"):
                    base_prompt += "- Specialty-Fokus: Ja\n"
                if roaster.get("price_position"):
                    base_prompt += (
                        f"- Preispositionierung: {roaster['price_position']}\n"
                    )

        base_prompt += "\n=== ENDE DER DATEN ===\n"
        return base_prompt
