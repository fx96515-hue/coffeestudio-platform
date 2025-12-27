# Changelog — CoffeeStudio OptionD

## v0.3.0-data — Data Backbone (News/Regions/Enrich/Dedup/Logistics/Outreach)

### Added
- New DB tables: `news_items`, `peru_regions`, `web_extracts`, `entity_aliases`, `entity_events`.
- Data APIs:
  - `GET/POST /news` (refresh + list)
  - `GET/POST /regions/peru` (seed + list)
  - `POST /enrich/{entity_type}/{id}` (web fetch + optional LLM extraction)
  - `GET /dedup/suggest` (duplicate suggestions)
  - `POST /logistics/landed-cost` (landed cost calculator)
  - `POST /outreach/generate` (email drafts)
  - `GET/POST /kb` (editable logistics/customs KB docs)
  - `GET/POST /cuppings` (SCA-style cupping results)
- Celery beat schedule extended: `refresh_news` uses `NEWS_REFRESH_TIMES`.

### Changed
- `.env.example` extended with freshness defaults + refresh times.
- `README_WINDOWS.md` extended with optional Data-Gates A-E.

### Notes
- Perplexity-backed features stay optional; without `PERPLEXITY_API_KEY` the app runs and news/enrich LLM parts return `skipped`.

## v0.2.1c — Auth/Bootstrap Fix (pbkdf2) + Windows-first env

### Fixed
- Eliminated `/auth/dev/bootstrap` 500 caused by `passlib`/`bcrypt` backend incompatibility (bcrypt 4.x API change).
- Frontend default login email is now a valid email (`admin@coffeestudio.com`).

### Changed
- Password hashing switched to `pbkdf2_sha256` (stable, no native bcrypt bindings).
- `docker-compose.yml` now uses `env_file: ./.env` for consistent environment handling.
- Backend starts with `alembic upgrade head` before `uvicorn` to ensure migrations are always applied.
- Added backend healthcheck (Compose service_healthy gating for frontend/worker/beat).

### Added
- `README_WINDOWS.md` with explicit Gates 0-9.

### Security
- `.env.example` contains no real secrets; local `run_windows.ps1` generates JWT secret and sets dev bootstrap password in the local `.env`.

## 0.3.2-maxstack (2025-12-23)
- MAX stack: Traefik single-entrypoint, Portainer, Grafana+Prometheus+Loki+Tempo, Blackbox, cAdvisor, node-exporter.
- MAX automation: n8n workflows, Keycloak (dev), LLM stack (Ollama + Open WebUI + LiteLLM), Langfuse observability.
- Ops: WUD update dashboard + optional Watchtower.
- Windows: stepwise runner with automatic backups + diagnostics + guided troubleshooting.
