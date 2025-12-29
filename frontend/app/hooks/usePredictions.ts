import { useQuery, useMutation } from "@tanstack/react-query";
import { apiFetch } from "../../lib/api";
import {
  FreightPredictionRequest,
  FreightPredictionResponse,
  PricePredictionRequest,
  PricePredictionResponse,
} from "../types";

// Freight Cost Prediction
export function useFreightPrediction() {
  return useMutation({
    mutationFn: async (data: FreightPredictionRequest) => {
      return await apiFetch<FreightPredictionResponse>("/ml/predict-freight", {
        method: "POST",
        body: JSON.stringify(data),
      });
    },
  });
}

// Coffee Price Prediction
export function usePricePrediction() {
  return useMutation({
    mutationFn: async (data: PricePredictionRequest) => {
      // Map frontend field names to backend API
      const parts = data.origin.split(",");
      const origin_country = parts[0]?.trim() || data.origin;
      const origin_region = parts.length > 1 ? parts[1]?.trim() || "" : "";
      
      const backendRequest = {
        origin_country,
        origin_region,
        variety: data.variety,
        process_method: data.process,
        quality_grade: data.grade,
        cupping_score: data.cupping_score,
        certifications: data.certifications,
        forecast_date: data.forecast_date,
      };
      return await apiFetch<PricePredictionResponse>("/ml/predict-coffee-price", {
        method: "POST",
        body: JSON.stringify(backendRequest),
      });
    },
  });
}

// Fetch freight cost trend
export function useFreightCostTrend(params?: { route?: string; months_back?: number }) {
  const searchParams = new URLSearchParams();
  if (params?.route) searchParams.set("route", params.route);
  if (params?.months_back) searchParams.set("months_back", String(params.months_back));

  return useQuery({
    queryKey: ["freight-cost-trend", params],
    queryFn: async () => {
      const data = await apiFetch<any>(`/ml/freight-cost-trend?${searchParams.toString()}`);
      return data;
    },
    enabled: !!params?.route,
  });
}

// Fetch historical freight data (legacy endpoint for backward compat)
export function useFreightHistory(params?: { route?: string; months?: number }) {
  const searchParams = new URLSearchParams();
  if (params?.route) searchParams.set("route", params.route);
  if (params?.months) searchParams.set("months_back", String(params.months));

  return useQuery({
    queryKey: ["freight-history", params],
    queryFn: async () => {
      const data = await apiFetch<any>(`/ml/freight-cost-trend?${searchParams.toString()}`);
      return data;
    },
    enabled: !!params?.route,
  });
}

// Fetch historical price data
export function usePriceHistory(params?: { origin?: string; months?: number }) {
  const searchParams = new URLSearchParams();
  if (params?.origin) searchParams.set("origin_region", params.origin);
  if (params?.months) searchParams.set("months_ahead", String(params.months));

  return useQuery({
    queryKey: ["price-history", params],
    queryFn: async () => {
      const data = await apiFetch<any>(`/ml/forecast-price-trend?${searchParams.toString()}`);
      return data;
    },
  });
}

// List ML models
export function useMLModels(modelType?: string) {
  const params = new URLSearchParams();
  if (modelType) params.set("model_type", modelType);

  return useQuery({
    queryKey: ["ml-models", modelType],
    queryFn: async () => {
      const data = await apiFetch<any[]>(`/ml/models?${params.toString()}`);
      return data;
    },
  });
}
