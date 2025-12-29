// TypeScript types matching backend Pydantic schemas

// Peru Regions
export interface PeruRegion {
  id: number;
  code: string;
  name: string;
  description_de: string | null;
  altitude_range: string | null;
  typical_varieties: string | null;
  typical_processing: string | null;
  logistics_notes: string | null;
  risk_notes: string | null;
}

// Cooperatives
export interface Cooperative {
  id: number;
  name: string;
  country: string;
  region: string | null;
  members_count: number | null;
  annual_production_kg: number | null;
  certifications: string[];
  contact_email: string | null;
  contact_phone: string | null;
  website_url: string | null;
  quality_score: number | null;
  reliability_score: number | null;
  economic_score: number | null;
  overall_score: number | null;
  next_action: string | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

// Roasters
export interface Roaster {
  id: number;
  company_name: string;
  city: string | null;
  state: string | null;
  country: string;
  roaster_type: string | null;
  annual_capacity_kg: number | null;
  certifications: string[];
  website_url: string | null;
  contact_email: string | null;
  contact_phone: string | null;
  sales_fit_score: number | null;
  contact_status: string | null;
  last_contact_date: string | null;
  next_followup_date: string | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

// Shipments/Logistics
export interface Shipment {
  id: number;
  reference: string;
  lot_id: number | null;
  origin_port: string;
  destination_port: string;
  departure_date: string | null;
  eta: string | null;
  actual_arrival: string | null;
  status: string;
  carrier: string | null;
  container_number: string | null;
  weight_kg: number | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface ShipmentEvent {
  id: number;
  shipment_id: number;
  event_type: string;
  event_date: string;
  location: string | null;
  description: string | null;
  created_at: string;
}

// Deals/Margins
export interface Deal {
  id: number;
  reference: string;
  cooperative_id: number | null;
  roaster_id: number | null;
  lot_id: number | null;
  quantity_kg: number;
  purchase_price_per_kg: number;
  purchase_currency: string;
  sale_price_per_kg: number;
  sale_currency: string;
  freight_cost: number;
  insurance_cost: number;
  other_costs: number;
  margin_eur: number | null;
  margin_percentage: number | null;
  stage: string;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface MarginCalcRequest {
  purchase_price_per_kg: number;
  purchase_currency: string;
  landed_costs_per_kg: number;
  roast_and_pack_costs_per_kg: number;
  yield_factor: number;
  selling_price_per_kg: number;
  selling_currency: string;
  fx_usd_to_eur?: number | null;
}

export interface MarginCalcResult {
  computed_at: string;
  inputs: Record<string, any>;
  outputs: Record<string, any>;
}

// ML Predictions
export interface FreightPredictionRequest {
  origin_port: string;
  destination_port: string;
  weight_kg: number;
  container_type: string;
  departure_date: string;
}

export interface FreightPredictionResponse {
  predicted_cost: number;
  confidence_score: number;
  confidence_interval: {
    lower: number;
    upper: number;
  };
  model_version: string;
}

export interface PricePredictionRequest {
  origin: string;
  variety: string;
  process: string;
  grade: string;
  cupping_score: number;
  certifications: string[];
  forecast_date: string;
}

export interface PricePredictionResponse {
  predicted_price: number;
  confidence_score: number;
  price_trend: string;
  forecast_period: string;
}

// News
export interface NewsItem {
  id: number;
  topic: string;
  title: string;
  source: string | null;
  url: string | null;
  published_at: string | null;
  created_at: string;
}

// Reports
export interface Report {
  id: number;
  name: string;
  kind: string;
  status: string;
  report_at: string;
  content: string | null;
}

// Market Data
export interface MarketPoint {
  value: number;
  unit?: string | null;
  currency?: string | null;
  observed_at: string;
}

export interface MarketSnapshot {
  [key: string]: MarketPoint | null;
}

// Pagination
export interface Paged<T> {
  items: T[];
  total: number;
  page?: number;
  limit?: number;
}

// Filters
export interface RegionFilters {
  min_production?: number;
  max_distance_to_callao?: number;
  min_cupping_score?: number;
}

export interface CooperativeFilters {
  region?: string;
  min_capacity?: number;
  max_capacity?: number;
  certifications?: string[];
  min_score?: number;
  contact_status?: string;
}

export interface RoasterFilters {
  city?: string;
  country?: string;
  roaster_type?: string;
  min_capacity?: number;
  max_capacity?: number;
  certifications?: string[];
  min_sales_fit_score?: number;
  contact_status?: string;
}

export interface ShipmentFilters {
  status?: string;
  origin_port?: string;
  destination_port?: string;
  date_from?: string;
  date_to?: string;
}

export interface DealFilters {
  stage?: string;
  cooperative_id?: number;
  roaster_id?: number;
  min_margin?: number;
  date_from?: string;
  date_to?: string;
}
