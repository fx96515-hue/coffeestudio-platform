# Quick Start Guide - Peru Sourcing Intelligence System

## Initial Setup

### 1. Run Database Migration
```bash
docker compose exec backend alembic upgrade head
```

### 2. Seed Peru Regions
```bash
# Get admin token first
TOKEN=$(curl -s -X POST http://localhost:8000/auth/dev/bootstrap | jq -r '.token')

# Seed regions
curl -X POST http://localhost:8000/peru/regions/seed \
  -H "Authorization: Bearer $TOKEN"
```

## Basic Usage

### List All Regions
```bash
curl http://localhost:8000/peru/regions \
  -H "Authorization: Bearer $TOKEN"
```

### Get Region Intelligence
```bash
# Get detailed info for Cajamarca
curl http://localhost:8000/peru/regions/Cajamarca/intelligence \
  -H "Authorization: Bearer $TOKEN"
```

### Analyze a Cooperative
```bash
# Analyze cooperative with ID 1
curl http://localhost:8000/peru/cooperatives/1/sourcing-analysis \
  -H "Authorization: Bearer $TOKEN"
```

### Force Fresh Analysis
```bash
curl -X POST http://localhost:8000/peru/cooperatives/1/analyze \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"force_refresh": true}'
```

## Sample Cooperative Data

To get meaningful results, populate a cooperative with sourcing intelligence data:

```bash
# Update cooperative with operational data
curl -X PATCH http://localhost:8000/cooperatives/1 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "operational_data": {
      "farmer_count": 180,
      "total_hectares": 450,
      "storage_capacity_kg": 100000,
      "has_wet_mill": true,
      "has_dry_mill": false
    },
    "export_readiness": {
      "export_license_number": "EXPORT-12345",
      "export_license_expiry": "2026-12-31",
      "senasa_registered": true,
      "customs_clearance_issues_count": 0,
      "has_document_coordinator": true,
      "export_experience_years": 6
    },
    "financial_data": {
      "annual_revenue_usd": 500000,
      "export_volume_kg_last_year": 25000,
      "avg_price_achieved_usd_per_kg": 5.20
    },
    "communication_metrics": {
      "avg_email_response_time_hours": 24,
      "languages_spoken": ["spanish", "english"],
      "missed_meetings_count": 0
    }
  }'
```

## Understanding Results

### Sourcing Analysis Response
```json
{
  "cooperative_id": 1,
  "cooperative_name": "Example Cooperative",
  "supply_capacity": {
    "score": 75.0,
    "details": {...}
  },
  "export_readiness": {
    "score": 90.0,
    "details": {...}
  },
  "communication_score": 85.0,
  "price_benchmark": {
    "score": 96.0,
    "details": {...}
  },
  "risk_assessment": {
    "risk_score": 38.0,
    "risk_factors": [...]
  },
  "total_score": 80.2,
  "recommendation": "RECOMMENDED"
}
```

### Score Interpretation
- **Total Score**: 0-100 (higher is better)
  - 80-100: Excellent
  - 70-79: Good
  - 60-69: Acceptable
  - <60: Poor

- **Risk Score**: 0-100 (lower is better)
  - 0-30: Low risk
  - 30-50: Moderate risk
  - 50-70: High risk
  - >70: Very high risk

### Recommendations
- **HIGHLY RECOMMENDED**: Score ≥80, Risk <30
- **RECOMMENDED**: Score ≥70, Risk <40
- **CONSIDER WITH CAUTION**: Score ≥60, Risk <50
- **MONITOR CLOSELY**: Moderate scores
- **NOT RECOMMENDED**: Score <60 or Risk ≥60

## Testing

### Run Unit Tests
```bash
docker compose exec backend pytest backend/tests/test_supply_capacity_scoring.py -v
docker compose exec backend pytest backend/tests/test_export_readiness_check.py -v
docker compose exec backend pytest backend/tests/test_risk_calculation.py -v
docker compose exec backend pytest backend/tests/test_price_benchmarking.py -v
```

### Run All Tests
```bash
docker compose exec backend pytest backend/tests/ -v
```

## Troubleshooting

### Migration Issues
```bash
# Check current migration version
docker compose exec backend alembic current

# View migration history
docker compose exec backend alembic history
```

### API Not Responding
```bash
# Check backend logs
docker compose logs backend

# Check if backend is running
docker compose ps backend
```

### Authentication Issues
```bash
# Bootstrap admin user
curl -X POST http://localhost:8000/auth/dev/bootstrap

# Login manually
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@coffeestudio.com&password=adminadmin"
```

## Next Steps

1. Integrate real external APIs (JNC, MINAGRI, SENAMHI, ICO)
2. Populate existing cooperatives with sourcing intelligence data
3. Set up monitoring and alerts for risk changes
4. Build frontend UI for visualizing scores and recommendations
5. Export data to spreadsheets for offline analysis

## Documentation

For detailed information, see:
- `docs/PERU_SOURCING_INTELLIGENCE.md` - Complete feature documentation
- `IMPLEMENTATION_SUMMARY.md` - Technical implementation details
