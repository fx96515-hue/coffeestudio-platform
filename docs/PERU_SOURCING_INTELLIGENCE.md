# Peru Sourcing Intelligence System

## Overview

The Peru Sourcing Intelligence System is a comprehensive buyer-side tool designed to enable data-driven cooperative selection and risk assessment for coffee buyers sourcing from Peru.

## Business Context

- **Use Case:** Buyer perspective (purchasing green coffee FROM Peru cooperatives)
- **Goal:** Minimize risk, optimize supplier selection, ensure export readiness
- **Target Users:** Coffee traders/importers sourcing from Peru to Germany

## Scoring Algorithms

### Supply Capacity Score (0-100, 30% of total)
- Volume: 30 points (based on annual export volume)
- Farmer count: 20 points
- Storage capacity: 20 points
- Processing facilities: 15 points (wet mill +8, dry mill +7)
- Export experience: 15 points

### Export Readiness Score (0-100, 20% of total)
- Export license valid: 25 points
- SENASA registered: 25 points
- Certifications: 25 points
- Customs history: 15 points
- Document coordinator: 10 points

### Communication Quality Score (0-100, 10% of total)
- Response time: 25 points (≤24h=25, ≤48h=20, ≤72h=10)
- Language skills: 25 points (English +15, German +10)
- Digital presence: 20 points
- Documentation quality: 15 points
- Meeting reliability: 15 points

### Price Competitiveness (0-100, 15% of total)
- Score: 100 - (abs(price_difference_pct) * 2)
- Compares cooperative FOB vs regional benchmark

### Risk Score (0-100, lower is better)
- Financial stability: max 25 points
- Quality consistency: max 20 points
- Delivery reliability: max 25 points
- Geographic factors: max 15 points
- Communication: max 15 points

### Total Score
Weighted average:
- Supply: 30%
- Quality track record: 25%
- Export readiness: 20%
- Price: 15%
- Communication: 10%

## API Endpoints

### Regions
- `GET /api/v1/peru/regions` - List all regions
- `GET /api/v1/peru/regions/{name}/intelligence` - Get region details
- `POST /api/v1/peru/regions/seed` - Seed regions data
- `POST /api/v1/peru/regions/refresh` - Refresh from external sources

### Cooperatives
- `GET /api/v1/peru/cooperatives/{id}/sourcing-analysis` - Get analysis
- `POST /api/v1/peru/cooperatives/{id}/analyze` - Force fresh analysis

## Usage Examples

### Initial Setup
```bash
# Run migrations
docker compose exec backend alembic upgrade head

# Seed regions
curl -X POST http://localhost:8000/peru/regions/seed \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Analyze Cooperative
```bash
# Get analysis
curl http://localhost:8000/peru/cooperatives/1/sourcing-analysis \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Data Sources

Currently implemented as stubs (TODO: integrate real APIs):
- JNC (Junta Nacional del Café) - Production data
- MINAGRI (Ministry of Agriculture) - Agricultural statistics
- SENAMHI (Weather Service) - Climate data
- ICO (International Coffee Organization) - Price data

## Peru Coffee Regions

### Cajamarca
- 30% national production
- 1200-2100 masl
- Typical score: 84
- Logistics: Fair, 870km to Callao

### Junín
- 20% national production
- 1000-1800 masl
- BEST logistics (320km to Callao)
- Typical score: 83

### San Martín
- 18% national production
- 800-1500 masl
- High humidity challenges
- Typical score: 81

### Cusco
- 15% national production
- 1500-2200 masl
- High quality potential
- Typical score: 86

### Amazonas
- 8% national production
- 1200-2100 masl
- Micro-lots specialty
- Typical score: 85

### Puno
- 5% national production
- 1300-2000 masl
- Very sweet, floral profiles
- Typical score: 87

## Recommendation System

- **HIGHLY RECOMMENDED:** Total ≥80 AND risk <30
- **RECOMMENDED:** Total ≥70 AND risk <40
- **CONSIDER WITH CAUTION:** Total ≥60 AND risk <50
- **MONITOR CLOSELY:** Moderate scores
- **NOT RECOMMENDED:** Total <60 OR risk ≥60
