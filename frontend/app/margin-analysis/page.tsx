"use client";

import { useState } from "react";
import KpiCard from "../components/KpiCard";
import Badge from "../components/Badge";

type MarginForm = {
  purchase_price_per_kg: string;
  purchase_currency: string;
  landed_costs_per_kg: string;
  roast_and_pack_costs_per_kg: string;
  yield_factor: string;
  selling_price_per_kg: string;
  selling_currency: string;
};

type MarginResult = {
  totalCostPerKgGreen: string;
  totalCostPerKgRoasted: string;
  marginPerKg: string;
  marginPct: string;
  breakeven: string;
};

export default function MarginAnalysisPage() {
  const [calculating, setCalculating] = useState(false);
  const [result, setResult] = useState<MarginResult | null>(null);
  const [form, setForm] = useState<MarginForm>({
    purchase_price_per_kg: "5.50",
    purchase_currency: "USD",
    landed_costs_per_kg: "0.80",
    roast_and_pack_costs_per_kg: "2.00",
    yield_factor: "0.84",
    selling_price_per_kg: "15.00",
    selling_currency: "EUR",
  });

  const handleCalculate = async () => {
    setCalculating(true);
    setResult(null);
    try {
      // Validate inputs
      const purchase = parseFloat(form.purchase_price_per_kg);
      const landed = parseFloat(form.landed_costs_per_kg);
      const roast = parseFloat(form.roast_and_pack_costs_per_kg);
      const yieldFactor = parseFloat(form.yield_factor);
      const selling = parseFloat(form.selling_price_per_kg);
      
      // Validation checks
      if (isNaN(purchase) || purchase <= 0) {
        throw new Error("Purchase price must be a positive number");
      }
      if (isNaN(landed) || landed < 0) {
        throw new Error("Landed costs must be zero or positive");
      }
      if (isNaN(roast) || roast < 0) {
        throw new Error("Roast & pack costs must be zero or positive");
      }
      if (isNaN(yieldFactor) || yieldFactor <= 0 || yieldFactor > 1) {
        throw new Error("Yield factor must be between 0 and 1");
      }
      if (isNaN(selling) || selling <= 0) {
        throw new Error("Selling price must be a positive number");
      }
      
      // Mock calculation for now - would call backend API
      await new Promise(resolve => setTimeout(resolve, 500));
      
      const totalCostPerKgGreen = purchase + landed;
      const totalCostPerKgRoasted = (totalCostPerKgGreen / yieldFactor) + roast;
      const marginPerKg = selling - totalCostPerKgRoasted;
      const marginPct = (marginPerKg / selling) * 100;
      
      setResult({
        totalCostPerKgGreen: totalCostPerKgGreen.toFixed(2),
        totalCostPerKgRoasted: totalCostPerKgRoasted.toFixed(2),
        marginPerKg: marginPerKg.toFixed(2),
        marginPct: marginPct.toFixed(1),
        breakeven: totalCostPerKgRoasted.toFixed(2),
      });
    } catch (error: any) {
      alert(error.message || "Invalid input values");
    } finally {
      setCalculating(false);
    }
  };

  return (
    <div className="page">
      <div className="pageHeader">
        <div>
          <div className="h1">Margin Analysis</div>
          <div className="muted">Calculate deal profitability and pricing scenarios</div>
        </div>
      </div>

      <div className="grid2">
        <div className="panel" style={{ padding: 18 }}>
          <div className="panelTitle" style={{ marginBottom: 16 }}>Margin Calculator</div>
          
          <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            <div>
              <label htmlFor="purchase-price" className="muted" style={{ fontSize: 12, display: "block", marginBottom: 4 }}>
                Purchase Price per kg
              </label>
              <div className="row gap">
                <input
                  id="purchase-price"
                  className="input"
                  type="number"
                  step="0.01"
                  value={form.purchase_price_per_kg}
                  onChange={(e) => setForm({ ...form, purchase_price_per_kg: e.target.value })}
                  style={{ flex: 1 }}
                />
                <select
                  className="input"
                  value={form.purchase_currency}
                  onChange={(e) => setForm({ ...form, purchase_currency: e.target.value })}
                  style={{ width: 100 }}
                >
                  <option>USD</option>
                  <option>EUR</option>
                </select>
              </div>
            </div>

            <div>
              <label htmlFor="landed-costs" className="muted" style={{ fontSize: 12, display: "block", marginBottom: 4 }}>
                Landed Costs per kg (freight, insurance, handling)
              </label>
              <input
                id="landed-costs"
                className="input"
                type="number"
                step="0.01"
                value={form.landed_costs_per_kg}
                onChange={(e) => setForm({ ...form, landed_costs_per_kg: e.target.value })}
              />
            </div>

            <div>
              <label htmlFor="roast-costs" className="muted" style={{ fontSize: 12, display: "block", marginBottom: 4 }}>
                Roast & Pack Costs per kg
              </label>
              <input
                id="roast-costs"
                className="input"
                type="number"
                step="0.01"
                value={form.roast_and_pack_costs_per_kg}
                onChange={(e) => setForm({ ...form, roast_and_pack_costs_per_kg: e.target.value })}
              />
            </div>

            <div>
              <label htmlFor="yield-factor" className="muted" style={{ fontSize: 12, display: "block", marginBottom: 4 }}>
                Yield Factor (green to roasted, e.g., 0.84 = 16% loss)
              </label>
              <input
                id="yield-factor"
                className="input"
                type="number"
                step="0.01"
                value={form.yield_factor}
                onChange={(e) => setForm({ ...form, yield_factor: e.target.value })}
              />
            </div>

            <div>
              <label htmlFor="selling-price" className="muted" style={{ fontSize: 12, display: "block", marginBottom: 4 }}>
                Selling Price per kg (roasted)
              </label>
              <div className="row gap">
                <input
                  id="selling-price"
                  className="input"
                  type="number"
                  step="0.01"
                  value={form.selling_price_per_kg}
                  onChange={(e) => setForm({ ...form, selling_price_per_kg: e.target.value })}
                  style={{ flex: 1 }}
                />
                <select
                  className="input"
                  value={form.selling_currency}
                  onChange={(e) => setForm({ ...form, selling_currency: e.target.value })}
                  style={{ width: 100 }}
                >
                  <option>EUR</option>
                  <option>USD</option>
                </select>
              </div>
            </div>

            <div className="muted" style={{ fontSize: 12 }}>
              Note: Calculation assumes same currency for all values. Currency conversion not applied.
            </div>

            <button
              className="btn btnPrimary"
              onClick={handleCalculate}
              disabled={calculating}
              style={{ marginTop: 8 }}
            >
              {calculating ? "Calculating..." : "Calculate Margin"}
            </button>
          </div>
        </div>

        <div className="panel" style={{ padding: 18 }}>
          <div className="panelTitle" style={{ marginBottom: 16 }}>Results</div>
          
          {result ? (
            <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
              <KpiCard
                label="Total Cost (Green Coffee)"
                value={`${result.totalCostPerKgGreen} ${form.purchase_currency}/kg`}
                hint="Purchase + Landed Costs"
              />
              <KpiCard
                label="Total Cost (Roasted)"
                value={`${result.totalCostPerKgRoasted} ${form.purchase_currency}/kg`}
                hint="After yield loss & roasting (same currency as purchase, no FX conversion)"
              />
              <KpiCard
                label="Margin per kg"
                value={`${result.marginPerKg} ${form.selling_currency}`}
                hint={`${result.marginPct}% margin`}
              />
              <KpiCard
                label="Breakeven Price"
                value={`${result.breakeven} ${form.selling_currency}/kg`}
                hint="Minimum selling price"
              />
              
              <div style={{ marginTop: 8 }}>
                <Badge tone={parseFloat(result.marginPct) > 20 ? "good" : parseFloat(result.marginPct) > 10 ? "warn" : "bad"}>
                  {parseFloat(result.marginPct) > 20 ? "Excellent Margin" : parseFloat(result.marginPct) > 10 ? "Good Margin" : "Low Margin"}
                </Badge>
              </div>
            </div>
          ) : (
            <div className="muted" style={{ textAlign: "center", padding: 32 }}>
              Enter values and click Calculate to see results
            </div>
          )}
        </div>
      </div>

      <div className="panel" style={{ padding: 18, marginTop: 18 }}>
        <div className="panelTitle">Cost Breakdown</div>
        <div className="muted" style={{ marginTop: 8 }}>
          Visual cost breakdown chart coming soon...
        </div>
      </div>
    </div>
  );
}
