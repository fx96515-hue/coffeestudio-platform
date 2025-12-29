"use client";

import { useState } from "react";
import { useFreightPrediction, usePricePrediction } from "../hooks/usePredictions";
import { useCooperatives } from "../hooks/usePeruRegions";
import { useRoasters } from "../hooks/useRoasters";
import LineChart from "../charts/LineChart";

export default function AnalyticsDashboard() {
  const [freightForm, setFreightForm] = useState({
    origin_port: "Callao",
    destination_port: "Hamburg",
    weight_kg: 18000,
    container_type: "20ft",
    departure_date: new Date().toISOString().split("T")[0],
  });

  const [priceForm, setPriceForm] = useState({
    origin: "Peru",
    variety: "Arabica",
    process: "Washed",
    grade: "SHG",
    cupping_score: 85,
    certifications: ["Organic"],
    forecast_date: new Date().toISOString().split("T")[0],
  });

  const freightMutation = useFreightPrediction();
  const priceMutation = usePricePrediction();

  const { data: coopsData } = useCooperatives({ limit: 5 });
  const { data: roastersData } = useRoasters({ country: "Germany", limit: 5 });

  const handleFreightPredict = () => {
    freightMutation.mutate(freightForm);
  };

  const handlePricePredict = () => {
    priceMutation.mutate(priceForm);
  };

  return (
    <div className="page">
      <div className="pageHeader">
        <div>
          <div className="h1">Analytics & ML Predictions</div>
          <div className="muted">
            Use machine learning models to predict freight costs, coffee prices, and trends
          </div>
        </div>
      </div>

      {/* Business Intelligence Cards */}
      <div className="grid gridCols4" style={{ marginBottom: "18px" }}>
        <div className="panel card">
          <div className="cardLabel">Active Cooperatives</div>
          <div className="cardValue">{coopsData?.total || 0}</div>
          <div className="cardHint">In Peru sourcing database</div>
        </div>
        <div className="panel card">
          <div className="cardLabel">German Roasters</div>
          <div className="cardValue">{roastersData?.total || 0}</div>
          <div className="cardHint">In sales pipeline</div>
        </div>
        <div className="panel card">
          <div className="cardLabel">Avg Quality Score</div>
          <div className="cardValue">
            {coopsData?.items.length
              ? (
                  coopsData.items.reduce((sum, c) => sum + (c.quality_score || 0), 0) /
                  coopsData.items.length
                ).toFixed(1)
              : "–"}
          </div>
          <div className="cardHint">Cooperative quality</div>
        </div>
        <div className="panel card">
          <div className="cardLabel">Avg Sales Score</div>
          <div className="cardValue">
            {roastersData?.items.length
              ? (
                  roastersData.items.reduce((sum, r) => sum + (r.sales_fit_score || 0), 0) /
                  roastersData.items.length
                ).toFixed(1)
              : "–"}
          </div>
          <div className="cardHint">Roaster sales fit</div>
        </div>
      </div>

      <div className="grid gridCols2" style={{ marginBottom: "18px" }}>
        {/* Freight Cost Predictor */}
        <div className="panel" style={{ padding: "18px" }}>
          <div className="h2">Freight Cost Predictor</div>
          <div className="muted" style={{ marginBottom: "14px" }}>
            Predict shipping costs for coffee containers
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: "10px", marginBottom: "14px" }}>
            <div>
              <label style={{ fontSize: "12px", color: "var(--muted)", display: "block", marginBottom: "6px" }}>
                Origin Port
              </label>
              <input
                type="text"
                className="input"
                value={freightForm.origin_port}
                onChange={(e) => setFreightForm({ ...freightForm, origin_port: e.target.value })}
              />
            </div>
            <div>
              <label style={{ fontSize: "12px", color: "var(--muted)", display: "block", marginBottom: "6px" }}>
                Destination Port
              </label>
              <input
                type="text"
                className="input"
                value={freightForm.destination_port}
                onChange={(e) =>
                  setFreightForm({ ...freightForm, destination_port: e.target.value })
                }
              />
            </div>
            <div className="grid gridCols2" style={{ gap: "10px" }}>
              <div>
                <label style={{ fontSize: "12px", color: "var(--muted)", display: "block", marginBottom: "6px" }}>
                  Weight (kg)
                </label>
                <input
                  type="number"
                  className="input"
                  value={freightForm.weight_kg}
                  onChange={(e) =>
                    setFreightForm({ ...freightForm, weight_kg: Number(e.target.value) })
                  }
                />
              </div>
              <div>
                <label style={{ fontSize: "12px", color: "var(--muted)", display: "block", marginBottom: "6px" }}>
                  Container Type
                </label>
                <select
                  className="input"
                  value={freightForm.container_type}
                  onChange={(e) =>
                    setFreightForm({ ...freightForm, container_type: e.target.value })
                  }
                >
                  <option value="20ft">20ft</option>
                  <option value="40ft">40ft</option>
                </select>
              </div>
            </div>
            <div>
              <label style={{ fontSize: "12px", color: "var(--muted)", display: "block", marginBottom: "6px" }}>
                Departure Date
              </label>
              <input
                type="date"
                className="input"
                value={freightForm.departure_date}
                onChange={(e) =>
                  setFreightForm({ ...freightForm, departure_date: e.target.value })
                }
              />
            </div>
          </div>

          <button
            className="btn btnPrimary"
            onClick={handleFreightPredict}
            disabled={freightMutation.isPending}
            style={{ width: "100%" }}
          >
            {freightMutation.isPending ? "Predicting..." : "Predict Freight Cost"}
          </button>

          {freightMutation.isSuccess && freightMutation.data && (
            <div
              className="panel"
              style={{
                marginTop: "14px",
                padding: "14px",
                background: "rgba(87,134,255,0.08)",
                border: "1px solid rgba(87,134,255,0.25)",
              }}
            >
              <div style={{ fontWeight: "700", marginBottom: "8px" }}>Prediction Result</div>
              <div style={{ fontSize: "24px", fontWeight: "800", marginBottom: "8px" }}>
                ${freightMutation.data.predicted_cost.toLocaleString()}
              </div>
              <div style={{ fontSize: "13px", color: "var(--muted)" }}>
                Confidence: {(freightMutation.data.confidence_score * 100).toFixed(1)}%
              </div>
              {freightMutation.data.confidence_interval && (
                <div style={{ fontSize: "13px", color: "var(--muted)", marginTop: "4px" }}>
                  Range: ${freightMutation.data.confidence_interval.lower.toLocaleString()} - $
                  {freightMutation.data.confidence_interval.upper.toLocaleString()}
                </div>
              )}
            </div>
          )}

          {freightMutation.isError && (
            <div className="alert bad" style={{ marginTop: "14px" }}>
              <div className="alertTitle">Prediction Failed</div>
              <div className="alertText">
                {freightMutation.error?.message || "Could not predict freight cost"}
              </div>
            </div>
          )}
        </div>

        {/* Coffee Price Predictor */}
        <div className="panel" style={{ padding: "18px" }}>
          <div className="h2">Coffee Price Predictor</div>
          <div className="muted" style={{ marginBottom: "14px" }}>
            Predict coffee prices based on quality and characteristics
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: "10px", marginBottom: "14px" }}>
            <div className="grid gridCols2" style={{ gap: "10px" }}>
              <div>
                <label style={{ fontSize: "12px", color: "var(--muted)", display: "block", marginBottom: "6px" }}>
                  Origin
                </label>
                <input
                  type="text"
                  className="input"
                  value={priceForm.origin}
                  onChange={(e) => setPriceForm({ ...priceForm, origin: e.target.value })}
                />
              </div>
              <div>
                <label style={{ fontSize: "12px", color: "var(--muted)", display: "block", marginBottom: "6px" }}>
                  Variety
                </label>
                <input
                  type="text"
                  className="input"
                  value={priceForm.variety}
                  onChange={(e) => setPriceForm({ ...priceForm, variety: e.target.value })}
                />
              </div>
            </div>
            <div className="grid gridCols2" style={{ gap: "10px" }}>
              <div>
                <label style={{ fontSize: "12px", color: "var(--muted)", display: "block", marginBottom: "6px" }}>
                  Process
                </label>
                <select
                  className="input"
                  value={priceForm.process}
                  onChange={(e) => setPriceForm({ ...priceForm, process: e.target.value })}
                >
                  <option value="Washed">Washed</option>
                  <option value="Natural">Natural</option>
                  <option value="Honey">Honey</option>
                </select>
              </div>
              <div>
                <label style={{ fontSize: "12px", color: "var(--muted)", display: "block", marginBottom: "6px" }}>
                  Grade
                </label>
                <input
                  type="text"
                  className="input"
                  value={priceForm.grade}
                  onChange={(e) => setPriceForm({ ...priceForm, grade: e.target.value })}
                />
              </div>
            </div>
            <div>
              <label style={{ fontSize: "12px", color: "var(--muted)", display: "block", marginBottom: "6px" }}>
                Cupping Score
              </label>
              <input
                type="number"
                className="input"
                min="0"
                max="100"
                value={priceForm.cupping_score}
                onChange={(e) =>
                  setPriceForm({ ...priceForm, cupping_score: Number(e.target.value) })
                }
              />
            </div>
            <div>
              <label style={{ fontSize: "12px", color: "var(--muted)", display: "block", marginBottom: "6px" }}>
                Forecast Date
              </label>
              <input
                type="date"
                className="input"
                value={priceForm.forecast_date}
                onChange={(e) => setPriceForm({ ...priceForm, forecast_date: e.target.value })}
              />
            </div>
          </div>

          <button
            className="btn btnPrimary"
            onClick={handlePricePredict}
            disabled={priceMutation.isPending}
            style={{ width: "100%" }}
          >
            {priceMutation.isPending ? "Predicting..." : "Predict Price"}
          </button>

          {priceMutation.isSuccess && priceMutation.data && (
            <div
              className="panel"
              style={{
                marginTop: "14px",
                padding: "14px",
                background: "rgba(64,214,123,0.08)",
                border: "1px solid rgba(64,214,123,0.25)",
              }}
            >
              <div style={{ fontWeight: "700", marginBottom: "8px" }}>Prediction Result</div>
              <div style={{ fontSize: "24px", fontWeight: "800", marginBottom: "8px" }}>
                ${priceMutation.data.predicted_price.toFixed(2)}/kg
              </div>
              <div style={{ fontSize: "13px", color: "var(--muted)" }}>
                Confidence: {(priceMutation.data.confidence_score * 100).toFixed(1)}%
              </div>
              {priceMutation.data.price_trend && (
                <div style={{ fontSize: "13px", color: "var(--muted)", marginTop: "4px" }}>
                  Trend: {priceMutation.data.price_trend}
                </div>
              )}
            </div>
          )}

          {priceMutation.isError && (
            <div className="alert bad" style={{ marginTop: "14px" }}>
              <div className="alertTitle">Prediction Failed</div>
              <div className="alertText">
                {priceMutation.error?.message || "Could not predict price"}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Info Panel */}
      <div className="panel" style={{ padding: "18px" }}>
        <div className="h2">About ML Predictions</div>
        <div className="muted" style={{ marginTop: "10px" }}>
          These predictions are powered by machine learning models trained on historical data. The
          freight cost predictor uses historical shipping data to estimate container costs, while
          the coffee price predictor analyzes quality characteristics and market trends. All
          predictions include confidence scores to help you assess reliability.
        </div>
      </div>
    </div>
  );
}
