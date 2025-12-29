import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
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
      return await apiFetch<FreightPredictionResponse>("/ml/predict/freight", {
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
      return await apiFetch<PricePredictionResponse>("/ml/predict/price", {
        method: "POST",
        body: JSON.stringify(data),
      });
    },
  });
}

// Fetch historical freight data
export function useFreightHistory(params?: { route?: string; months?: number }) {
  const searchParams = new URLSearchParams();
  if (params?.route) searchParams.set("route", params.route);
  if (params?.months) searchParams.set("months", String(params.months));

  return useQuery({
    queryKey: ["freight-history", params],
    queryFn: async () => {
      const data = await apiFetch<any[]>(`/ml/freight-history?${searchParams.toString()}`);
      return data;
    },
  });
}

// Fetch historical price data
export function usePriceHistory(params?: { origin?: string; months?: number }) {
  const searchParams = new URLSearchParams();
  if (params?.origin) searchParams.set("origin", params.origin);
  if (params?.months) searchParams.set("months", String(params.months));

  return useQuery({
    queryKey: ["price-history", params],
    queryFn: async () => {
      const data = await apiFetch<any[]>(`/ml/price-history?${searchParams.toString()}`);
      return data;
    },
  });
}
