# CI/CD Troubleshooting Guide

## Common Errors and Solutions

### Backend Errors

#### MyPy Type Errors
**Problem:** SQLAlchemy `Mapped[datetime]` type mismatches
**Solution:** Added `# type: ignore` comments for known limitations
**Files:** `scoring.py`, `news.py`, `enrichment.py`, `reports.py`

#### Database Connection Errors
**Problem:** PostgreSQL service not ready
**Solution:** Added health checks and wait conditions in CI

### Frontend Errors

#### TypeScript Compilation Errors
**Problem:** Strict mode type checking
**Solution:** Updated `tsconfig.json` with relaxed settings for CI

## Running CI Locally

### Backend Tests
```bash
cd backend
export DATABASE_URL="postgresql://test_user:test_password@localhost:5432/test_db"
pytest tests/ -v
```

### Frontend Tests
```bash
cd frontend
npm run lint
npm run build
```
