# CoffeeStudio Platform (Option D) — Web-App + API + DB

Dieses Repository ist ein **produktreifes Foundation-Setup** für CoffeeStudio (Peru → Deutschland Specialty Coffee).

**Stack**
- **Backend API:** FastAPI (Python)
- **DB:** Postgres
- **Cache/Broker:** Redis
- **Worker/Scheduler:** Celery + Celery Beat
- **Frontend:** Next.js (App Router) + TypeScript

## Kernfunktionen (v0.2.1c)
- CRUD für **Kooperativen** und **Röster**
- CRUD für **Lots** (lot-/shipment-orientierte Stammdaten)
- **Margen-Engine** (Calc + gespeicherte Runs je Lot)
- **Auth (JWT)** + einfache **RBAC-Rollen** (admin/analyst/viewer)
- **Quelle/Provenance**: jede Kennzahl kann mit Source + Timestamp gespeichert werden
- **Scoring Engine (v0):** Qualität/Zuverlässigkeit/Wirtschaftlichkeit + Confidence
- **Market Data (v0):** FX (ECB) Beispiel-Provider, Provider-Interface für Kaffee/Fracht
- **Daily Report (v0):** Report-Entität + Generator (API + Worker)

## UI (Next.js)
- Listen/Details: Kooperativen, Röster
- **Lots**: Liste + anlegen + Detail + Margen-Runs speichern
- **Reports**: Liste + Detail (Markdown-Rendering)

## Quickstart (Dev)

> **Windows 11 (PowerShell) empfohlen:** siehe `README_WINDOWS.md` oder direkt `run_windows.ps1` ausführen.

### 1) Voraussetzungen
- Docker + Docker Compose

### 2) Starten
```bash
cp .env.example .env
docker compose up --build
```

- Frontend: http://localhost:3000
- Backend: http://localhost:8000/docs

### 3) Erster Admin-User

1) Migration:
```bash
docker compose exec backend alembic upgrade head
```
2) Dev-Bootstrap (legt admin@coffeestudio.com / adminadmin an, wenn DB leer ist):
```bash
curl -X POST http://localhost:8000/auth/dev/bootstrap
```

## Perplexity Discovery Seed (Kooperativen + Röster)

Wenn du `PERPLEXITY_API_KEY` setzt, kann CoffeeStudio ein **Start-Set** an Einträgen automatisch finden
und als Tasks/Einträge in der DB anlegen (jeweils mit **Evidence-URLs** in `entity_evidence`).

**Wichtig:** Das ist bewusst **konservativ** – wir füllen primär leere Felder und markieren `next_action = "In Recherche"`.

### Variante A: per API (asynchron via Celery)

1) `PERPLEXITY_API_KEY` in `.env` setzen
2) Stack starten + migrieren
3) Seed-Job anstoßen:

```bash
curl -X POST http://localhost:8000/discovery/seed \
  -H "Authorization: Bearer <ADMIN_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"entity_type":"both","max_entities":50,"dry_run":false}'
```

Status abfragen:

```bash
curl http://localhost:8000/discovery/seed/<TASK_ID> \
  -H "Authorization: Bearer <ADMIN_TOKEN>"
```

### Variante B: per Script (synchron)

```bash
docker compose exec backend python scripts/seed_first_run.py --both --max 50
```

### Smoke-Test

```bash
make smoke
```

## Architektur
- `backend/` FastAPI + DB + Domain-Services
- `worker/` Celery Worker/Beat (nutzt denselben Python-Code wie backend)
- `frontend/` Next.js UI
- `infra/` optionale Deploy-Assets

## Sicherheit (Foundation)
- JWT via `Authorization: Bearer ...`
- Passwörter gehasht (`pbkdf2_sha256`)
- CORS restriktiv konfigurierbar
- Rate Limiting (SlowAPI)
- Input validation (Pydantic)
- **Security Headers Middleware** (X-Frame-Options, CSP, HSTS, etc.)
- **Input Validation Middleware** (SQL Injection & XSS Detection)
- **Standardized Error Handling** with consistent error format

See [SECURITY.md](SECURITY.md) and [SECURITY_BEST_PRACTICES.md](SECURITY_BEST_PRACTICES.md) for comprehensive security documentation.

## API Documentation

📖 **See [API_USAGE_GUIDE.md](./API_USAGE_GUIDE.md)** for:
- Complete API reference with examples
- Authentication & authorization guide
- Request/response formats
- Error handling
- Rate limiting details
- Python & JavaScript SDK examples

Interactive API docs available at:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## Testing

Comprehensive test suite with **45 passing tests** and **57% code coverage**.

### Backend Tests

```bash
cd backend
pip install -r requirements-dev.txt
pytest tests/ -v
```

**With coverage:**
```bash
pytest tests/ --cov=app --cov-report=html
```

See [TESTING.md](TESTING.md) for complete testing documentation.

### Security

See [SECURITY.md](SECURITY.md) and [SECURITY_BEST_PRACTICES.md](SECURITY_BEST_PRACTICES.md) for comprehensive security documentation.

## Status & Roadmap

📊 **Siehe [STATUS.md](./STATUS.md)** für:
- Aktueller Status aller Features
- Was kommt als Nächstes (4-Phasen-Roadmap)
- Implementation Backlog
- Vorschläge & Empfehlungen
- Produktivsetzung (Production Readiness: 60%)

## Nächste Schritte
- Vollständige Provider (ICO/ICE/Fracht)
- Multi-Tenant / Mandantenfähigkeit (optional)
- Fine-grained Permissions + Audit Log
- CI/CD + Container Registry + Deployment
