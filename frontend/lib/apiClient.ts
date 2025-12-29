import { apiFetch } from "../lib/api";

// Types
export type Shipment = {
  id: number;
  lot_id: number;
  status: string;
  origin?: string | null;
  destination?: string | null;
  shipped_at?: string | null;
  estimated_arrival?: string | null;
  actual_arrival?: string | null;
};

export type ShipmentEvent = {
  id: number;
  shipment_id: number;
  event_type: string;
  location?: string | null;
  notes?: string | null;
  occurred_at: string;
};

export type Deal = {
  id: number;
  roaster_id: number;
  lot_id?: number | null;
  stage: string;
  value?: number | null;
  currency?: string | null;
  notes?: string | null;
  created_at: string;
  updated_at: string;
};

export type Communication = {
  id: number;
  roaster_id: number;
  communication_type: string;
  subject?: string | null;
  content?: string | null;
  sentiment?: string | null;
  occurred_at: string;
};

// Shipments API
export const shipmentsAPI = {
  list: async (params?: { status?: string; limit?: number }) => {
    const query = new URLSearchParams();
    if (params?.status) query.append("status", params.status);
    if (params?.limit) query.append("limit", String(params.limit));
    return apiFetch<Shipment[]>(`/shipments?${query}`);
  },
  
  get: async (id: number) => {
    return apiFetch<Shipment>(`/shipments/${id}`);
  },
  
  getEvents: async (shipmentId: number) => {
    return apiFetch<ShipmentEvent[]>(`/shipments/${shipmentId}/events`);
  },
};

// Deals API
export const dealsAPI = {
  list: async (params?: { stage?: string; limit?: number }) => {
    const query = new URLSearchParams();
    if (params?.stage) query.append("stage", params.stage);
    if (params?.limit) query.append("limit", String(params.limit));
    return apiFetch<Deal[]>(`/deals?${query}`);
  },
  
  get: async (id: number) => {
    return apiFetch<Deal>(`/deals/${id}`);
  },
  
  create: async (data: Partial<Deal>) => {
    return apiFetch<Deal>("/deals", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },
  
  update: async (id: number, data: Partial<Deal>) => {
    return apiFetch<Deal>(`/deals/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    });
  },
};

// Communications API
export const communicationsAPI = {
  list: async (roasterId?: number) => {
    const query = roasterId ? `?roaster_id=${roasterId}` : "";
    return apiFetch<Communication[]>(`/communications${query}`);
  },
  
  create: async (data: Partial<Communication>) => {
    return apiFetch<Communication>("/communications", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },
};

// Margins API
export const marginsAPI = {
  calculate: async (data: {
    purchase_price_per_kg: number;
    purchase_currency?: string;
    landed_costs_per_kg?: number;
    roast_and_pack_costs_per_kg?: number;
    yield_factor?: number;
    selling_price_per_kg: number;
    selling_currency?: string;
    fx_usd_to_eur?: number;
  }) => {
    return apiFetch<any>("/margins/calc", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },
  
  getRunsForLot: async (lotId: number) => {
    return apiFetch<any[]>(`/margins/lots/${lotId}/runs`);
  },
};

// Outreach API
export const outreachAPI = {
  generate: async (data: {
    entity_type: string;
    entity_id: number;
    language?: string;
    purpose?: string;
    counterpart_name?: string;
    refine_with_llm?: boolean;
  }) => {
    return apiFetch<{ status: string; email: any }>("/outreach/generate", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },
};

// Logistics API
export const logisticsAPI = {
  calculateLandedCost: async (data: {
    weight_kg: number;
    green_price_usd_per_kg: number;
    incoterm?: string;
    freight_usd?: number;
    insurance_pct?: number;
    handling_eur?: number;
    inland_trucking_eur?: number;
    duty_pct?: number;
    vat_pct?: number;
  }) => {
    return apiFetch<any>("/logistics/landed-cost", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },
};
