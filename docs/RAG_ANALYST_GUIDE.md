# RAG AI Analyst Guide

## Übersicht

Der RAG (Retrieval-Augmented Generation) KI-Analyst ist eine conversational AI für die CoffeeStudio-Plattform. Nutzer können in natürlicher Sprache (Deutsch/Englisch) Fragen über Kooperativen, Röstereien, Marktdaten und Sourcing stellen.

## Architektur

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (Next.js)                      │
│                  /analyst Chat Interface                    │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/JSON
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              Backend API (FastAPI)                          │
│           POST /analyst/ask                                 │
│           GET  /analyst/status                              │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│            RAGAnalystService                                │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  1. Question Embedding                               │  │
│  │     (via EmbeddingService)                           │  │
│  └───────────────────┬──────────────────────────────────┘  │
│                      ▼                                      │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  2. Context Retrieval                                │  │
│  │     (pgvector Similarity Search)                     │  │
│  │     - Top N Cooperatives                             │  │
│  │     - Top N Roasters                                 │  │
│  └───────────────────┬──────────────────────────────────┘  │
│                      ▼                                      │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  3. System Prompt Building                           │  │
│  │     (Context + Instructions)                         │  │
│  └───────────────────┬──────────────────────────────────┘  │
│                      ▼                                      │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  4. LLM Generation                                   │  │
│  │     (OpenAI GPT-4o-mini)                             │  │
│  │     System + History + Question → Answer             │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              PostgreSQL + pgvector                          │
│     cooperatives.embedding (HNSW Index)                     │
│     roasters.embedding (HNSW Index)                         │
└─────────────────────────────────────────────────────────────┘
```

## Komponenten

### Backend

#### 1. Service: `backend/app/services/rag_analyst.py`

**RAGAnalystService** - Hauptlogik für RAG-basierte Fragenbeantwortung

**Methoden:**
- `is_available()` - Prüft ob OpenAI API Key konfiguriert ist
- `ask(question, conversation_history, db)` - Beantwortet Fragen mit RAG
- `_retrieve_context(question, db)` - Holt relevante Entities via pgvector
- `_build_system_prompt(context)` - Baut System-Prompt mit Kontext

**Konfiguration:**
- Nutzt `settings.RAG_LLM_MODEL` (default: "gpt-4o-mini")
- Nutzt `settings.RAG_TEMPERATURE` (default: 0.3)
- Nutzt `settings.RAG_MAX_CONTEXT_ENTITIES` (default: 10)
- Nutzt `settings.RAG_MAX_CONVERSATION_HISTORY` (default: 20)

#### 2. API Routes: `backend/app/api/routes/rag_analyst.py`

**Endpoints:**

**POST /analyst/ask**
- Fragt den KI-Analysten
- Rate Limit: 20 Requests/Minute
- Authentifizierung: `require_auth` (alle authentifizierten Nutzer)
- Request Body: `RAGQuestion`
- Response: `RAGResponse`

**GET /analyst/status**
- Gibt Status des RAG Service zurück
- Authentifizierung: `require_auth`
- Response: `RAGStatusResponse`

#### 3. Schemas: `backend/app/schemas/rag_analyst.py`

**RAGQuestion**
```python
{
  "question": str,  # max 1000 chars
  "conversation_history": [
    {"role": "user" | "assistant", "content": str}
  ]  # max 20 messages
}
```

**RAGResponse**
```python
{
  "answer": str,
  "sources": [
    {
      "entity_type": "cooperative" | "roaster",
      "entity_id": int,
      "name": str,
      "similarity_score": float  # 0.0-1.0
    }
  ],
  "model": str,
  "tokens_used": int | None
}
```

**RAGStatusResponse**
```python
{
  "available": bool,
  "model": str,
  "embedding_model": str
}
```

### Frontend

#### Analyst Page: `frontend/app/analyst/page.tsx`

**Features:**
- Chat-Interface mit User/Assistant Messages
- Beispielfragen zum Anklicken
- Loading-Spinner während der Antwort
- Quellenangaben als klickbare Links
- Conversation History (automatisch mitgesendet)
- Error Handling und Service Status Check
- Responsive Design mit Kaffee-Theme

**Styled Components:**
- Warme Brauntöne passend zum CoffeeStudio-Design
- CSS-Variablen aus `globals.css`
- Mobile-friendly Layout

## API Beispiele

### Frage stellen

```bash
curl -X POST http://localhost:8000/analyst/ask \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Welche Kooperativen in Cajamarca haben Fair Trade Zertifizierung?",
    "conversation_history": []
  }'
```

**Response:**
```json
{
  "answer": "In Cajamarca gibt es mehrere Kooperativen mit Fair Trade Zertifizierung:\n\n1. **Cooperativa Agraria Cafetalera La Prosperidad** (ID: 123)\n   - Region: Cajamarca\n   - Zertifizierungen: Organic, Fair Trade\n   - Höhe: 1500m\n\n2. **Cooperativa Agraria Cafetalera San Ignacio** (ID: 456)...",
  "sources": [
    {
      "entity_type": "cooperative",
      "entity_id": 123,
      "name": "Cooperativa Agraria Cafetalera La Prosperidad",
      "similarity_score": 0.89
    },
    {
      "entity_type": "cooperative",
      "entity_id": 456,
      "name": "Cooperativa Agraria Cafetalera San Ignacio",
      "similarity_score": 0.85
    }
  ],
  "model": "gpt-4o-mini",
  "tokens_used": 450
}
```

### Status prüfen

```bash
curl -X GET http://localhost:8000/analyst/status \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
{
  "available": true,
  "model": "gpt-4o-mini",
  "embedding_model": "text-embedding-3-small"
}
```

### Mit Conversation History

```bash
curl -X POST http://localhost:8000/analyst/ask \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Welche davon sind in über 1600m Höhe?",
    "conversation_history": [
      {
        "role": "user",
        "content": "Welche Kooperativen in Cajamarca haben Fair Trade?"
      },
      {
        "role": "assistant",
        "content": "In Cajamarca gibt es mehrere Kooperativen..."
      }
    ]
  }'
```

## Konfiguration

### Umgebungsvariablen

In `.env` oder `.env.local`:

```bash
# Required: OpenAI API Key
OPENAI_API_KEY=sk-...

# Optional: RAG Configuration
RAG_LLM_MODEL=gpt-4o-mini          # LLM model to use
RAG_MAX_CONTEXT_ENTITIES=10        # Max entities for context
RAG_MAX_CONVERSATION_HISTORY=20    # Max conversation messages
RAG_TEMPERATURE=0.3                # LLM temperature (0.0-2.0)

# Required for embeddings
EMBEDDING_MODEL=text-embedding-3-small
```

### Settings in `backend/app/core/config.py`

```python
class Settings(BaseSettings):
    # OpenAI for embeddings and RAG
    OPENAI_API_KEY: str | None = None
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    
    # RAG AI Analyst
    RAG_LLM_MODEL: str = "gpt-4o-mini"
    RAG_MAX_CONTEXT_ENTITIES: int = 10
    RAG_MAX_CONVERSATION_HISTORY: int = 20
    RAG_TEMPERATURE: float = 0.3
```

## Frontend-Nutzung

1. **Zugriff:** Navigiere zu `/analyst` in der Sidebar unter "🤖 KI-Analyst"

2. **Beispielfragen:** Klicke auf eine der vorgeschlagenen Fragen:
   - "Welche Kooperativen in Cajamarca haben Fair Trade Zertifizierung?"
   - "Vergleiche Röstereien in München nach Bewertung"
   - "Was sind die besten Regionen für Specialty Coffee in Peru?"

3. **Eigene Fragen:** Tippe deine Frage ins Eingabefeld und klicke "Senden"

4. **Quellenangaben:** Klicke auf Quellenlinks um zu den Entity-Detailseiten zu gelangen

5. **Conversation History:** Die letzten 20 Nachrichten werden automatisch als Kontext mitgesendet

## Troubleshooting

### Service nicht verfügbar (503)

**Problem:** API gibt 503 zurück mit "RAG AI Analyst ist nicht verfügbar"

**Lösung:**
- Prüfe ob `OPENAI_API_KEY` in `.env` gesetzt ist
- Prüfe API Key Gültigkeit auf https://platform.openai.com/api-keys
- Restart Backend: `docker-compose restart backend`

### Keine Embeddings für Entities

**Problem:** Queries funktionieren nicht, da keine Embeddings vorhanden

**Lösung:**
```bash
# Embeddings für alle Cooperatives generieren
curl -X POST http://localhost:8000/enrich/cooperatives/embeddings \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"

# Embeddings für alle Roasters generieren
curl -X POST http://localhost:8000/enrich/roasters/embeddings \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

### Rate Limit erreicht

**Problem:** "Too Many Requests" Error

**Lösung:**
- Warte 1 Minute (Rate Limit: 20 Requests/Minute)
- Reduziere Anzahl der Anfragen
- Bei Bedarf: Erhöhe Limit in `backend/app/api/routes/rag_analyst.py`

### Schlechte Antwortqualität

**Problem:** Antworten sind ungenau oder irrelevant

**Mögliche Ursachen:**
1. **Zu wenig Kontext:** Erhöhe `RAG_MAX_CONTEXT_ENTITIES`
2. **Schlechte Embeddings:** Regeneriere Embeddings für Entities
3. **Falsches Modell:** Wechsle zu `gpt-4` für bessere Qualität (teurer)
4. **Zu kreativ:** Reduziere `RAG_TEMPERATURE` auf 0.1-0.2

**Anpassungen in `.env`:**
```bash
RAG_MAX_CONTEXT_ENTITIES=15
RAG_TEMPERATURE=0.2
RAG_LLM_MODEL=gpt-4  # Bessere Qualität, aber teurer
```

### OpenAI API Fehler

**Problem:** API gibt Fehler zurück (429, 500, etc.)

**Lösung:**
- 429 Rate Limit: Warte und versuche erneut
- 500 Server Error: Retry nach ein paar Sekunden
- 401 Unauthorized: API Key überprüfen
- Prüfe OpenAI Status: https://status.openai.com/

### Frontend zeigt "Fehler beim Verbinden"

**Problem:** Frontend kann Backend nicht erreichen

**Lösung:**
- Prüfe `NEXT_PUBLIC_API_URL` in Frontend `.env.local`
- Prüfe Backend läuft: `curl http://localhost:8000/health`
- Prüfe CORS Settings in Backend Config
- Prüfe Browser Console für Details

## Kosten und Performance

### Token-Kosten

- **Embeddings:** ~$0.0001 pro Request (text-embedding-3-small)
- **LLM Calls:** Variiert je nach Modell
  - gpt-4o-mini: ~$0.0003 per 1K input tokens, ~$0.0012 per 1K output tokens
  - gpt-4: ~$0.03 per 1K input tokens, ~$0.06 per 1K output tokens

**Typische Kosten pro Frage:**
- Embedding: ~$0.0001
- LLM (mit 5 Context Entities): ~$0.001-0.003 (gpt-4o-mini)
- **Total:** ~$0.001-0.003 pro Frage

### Performance Optimierung

1. **Cache häufige Fragen** (TODO: Redis Cache)
2. **Reduziere Context:** Weniger Entities = schneller + billiger
3. **Batch Embedding Generation:** Nutze Celery Tasks
4. **HNSW Index Tuning:** Optimiere pgvector Index Parameter

## Enterprise Roadmap

Siehe Issue #85 für geplante Features:
- Multi-Modal Support (PDFs, Bilder)
- Custom Knowledge Base Integration
- Advanced Analytics Dashboard
- Multi-Language Support (Spanisch, etc.)
- Voice Input/Output
- Export von Conversations

## Support

- **Technische Fragen:** Siehe [BACKEND_SETUP.md](../BACKEND_SETUP.md)
- **API Docs:** http://localhost:8000/docs (Swagger UI)
- **Logs:** `docker-compose logs backend` für Debugging
- **Issues:** GitHub Issues für Bug Reports

---

**Version:** 1.0.0  
**Letzte Aktualisierung:** 2026-02-13  
**Maintainer:** CoffeeStudio Platform Team
