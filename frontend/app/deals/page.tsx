"use client";

import { useState } from "react";
import Link from "next/link";
import { useDeals, useCalculateMargin } from "../hooks/useDeals";
import { MarginCalcRequest, Deal } from "../types";
import PieChart from "../charts/PieChart";

export default function DealsDashboard() {
  const [showCalculator, setShowCalculator] = useState(false);
  const [marginForm, setMarginForm] = useState<MarginCalcRequest>({
    purchase_price_per_kg: 4.5,
    purchase_currency: "USD",
    landed_costs_per_kg: 0.8,
    roast_and_pack_costs_per_kg: 1.2,
    yield_factor: 0.84,
    selling_price_per_kg: 12.0,
    selling_currency: "EUR",
  });

  const { data: dealsData, isLoading } = useDeals({ limit: 50 });
  const calculateMargin = useCalculateMargin();

  const deals = dealsData?.items || [];

  // Calculate overview stats (using lots as deals for now)
  const stats = {
    total: deals.length,
    totalValue: deals.reduce((sum, d) => sum + ((d as any).value_eur || 0), 0),
    avgMargin: 15.5, // Placeholder
  };

  const handleCalculate = () => {
    calculateMargin.mutate(marginForm);
  };

  // Mock cost breakdown data for chart
  const costBreakdown = [
    { name: "Purchase", value: marginForm.purchase_price_per_kg },
    { name: "Landed Costs", value: marginForm.landed_costs_per_kg },
    { name: "Roast & Pack", value: marginForm.roast_and_pack_costs_per_kg },
  ];

  return (
    <div className="page">
      <div className="pageHeader">
        <div>
          <div className="h1">Deals & Margin Calculator</div>
          <div className="muted">
            Manage deals, calculate margins, and analyze profitability
          </div>
        </div>
        <div className="actions">
          <button
            type="button"
            className="btn btnPrimary"
            onClick={() => setShowCalculator(!showCalculator)}
          >
            {showCalculator ? "Hide Calculator" : "Margin Calculator"}
          </button>
          <Link href="/lots" className="btn">
            View All Lots
          </Link>
        </div>
      </div>

      {/* Overview KPIs */}
      <div className="grid gridCols4" style={{ marginBottom: "18px" }}>
        <div className="panel card">
          <div className="cardLabel">Total Deals</div>
          <div className="cardValue">{stats.total}</div>
          <div className="cardHint">Active and completed</div>
        </div>
        <div className="panel card">
          <div className="cardLabel">Pipeline Value</div>
          <div className="cardValue">€{stats.totalValue.toLocaleString()}</div>
          <div className="cardHint">Total deal value</div>
        </div>
        <div className="panel card">
          <div className="cardLabel">Avg Margin</div>
          <div className="cardValue">{stats.avgMargin.toFixed(1)}%</div>
          <div className="cardHint">Average gross margin</div>
        </div>
        <div className="panel card">
          <div className="cardLabel">Active Lots</div>
          <div className="cardValue">{deals.filter((d) => (d as any).status !== "completed").length}</div>
          <div className="cardHint">In progress</div>
        </div>
      </div>

      {/* Margin Calculator */}
      {showCalculator && (
        <div className="panel" style={{ padding: "18px", marginBottom: "18px" }}>
          <div className="h2">Real-time Margin Calculator</div>
          <div className="muted" style={{ marginBottom: "14px" }}>
            Calculate profitability scenarios for coffee deals
          </div>

          <div className="grid gridCols2" style={{ gap: "18px" }}>
            {/* Input Form */}
            <div>
              <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
                <div>
                  <label style={{ fontSize: "12px", color: "var(--muted)", display: "block", marginBottom: "6px" }}>
                    Purchase Price per kg (USD)
                  </label>
                  <input
                    type="number"
                    step="0.1"
                    className="input"
                    value={marginForm.purchase_price_per_kg}
                    onChange={(e) =>
                      setMarginForm({
                        ...marginForm,
                        purchase_price_per_kg: Number(e.target.value),
                      })
                    }
                  />
                </div>
                <div>
                  <label style={{ fontSize: "12px", color: "var(--muted)", display: "block", marginBottom: "6px" }}>
                    Landed Costs per kg (EUR)
                  </label>
                  <input
                    type="number"
                    step="0.1"
                    className="input"
                    value={marginForm.landed_costs_per_kg}
                    onChange={(e) =>
                      setMarginForm({
                        ...marginForm,
                        landed_costs_per_kg: Number(e.target.value),
                      })
                    }
                  />
                  <div style={{ fontSize: "11px", color: "var(--muted)", marginTop: "4px" }}>
                    Includes freight, insurance, customs, handling
                  </div>
                </div>
                <div>
                  <label style={{ fontSize: "12px", color: "var(--muted)", display: "block", marginBottom: "6px" }}>
                    Roast & Pack Costs per kg (EUR)
                  </label>
                  <input
                    type="number"
                    step="0.1"
                    className="input"
                    value={marginForm.roast_and_pack_costs_per_kg}
                    onChange={(e) =>
                      setMarginForm({
                        ...marginForm,
                        roast_and_pack_costs_per_kg: Number(e.target.value),
                      })
                    }
                  />
                </div>
                <div>
                  <label style={{ fontSize: "12px", color: "var(--muted)", display: "block", marginBottom: "6px" }}>
                    Yield Factor (Green to Roasted)
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    min="0"
                    max="1"
                    className="input"
                    value={marginForm.yield_factor}
                    onChange={(e) =>
                      setMarginForm({ ...marginForm, yield_factor: Number(e.target.value) })
                    }
                  />
                  <div style={{ fontSize: "11px", color: "var(--muted)", marginTop: "4px" }}>
                    0.84 = 16% weight loss during roasting
                  </div>
                </div>
                <div>
                  <label style={{ fontSize: "12px", color: "var(--muted)", display: "block", marginBottom: "6px" }}>
                    Selling Price per kg (EUR)
                  </label>
                  <input
                    type="number"
                    step="0.1"
                    className="input"
                    value={marginForm.selling_price_per_kg}
                    onChange={(e) =>
                      setMarginForm({
                        ...marginForm,
                        selling_price_per_kg: Number(e.target.value),
                      })
                    }
                  />
                </div>
                <button
                  type="button"
                  className="btn btnPrimary"
                  onClick={handleCalculate}
                  disabled={calculateMargin.isPending}
                  style={{ marginTop: "10px" }}
                >
                  {calculateMargin.isPending ? "Calculating..." : "Calculate Margin"}
                </button>
              </div>
            </div>

            {/* Results & Charts */}
            <div>
              {calculateMargin.isSuccess && calculateMargin.data && (
                <div>
                  <div
                    className="panel"
                    style={{
                      padding: "18px",
                      background: "rgba(64,214,123,0.08)",
                      border: "1px solid rgba(64,214,123,0.25)",
                      marginBottom: "14px",
                    }}
                  >
                    <div style={{ fontWeight: "700", marginBottom: "12px" }}>Margin Results</div>
                    <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
                      {Object.entries(calculateMargin.data.outputs).map(([key, value]) => (
                        <div key={key} style={{ display: "flex", justifyContent: "space-between" }}>
                          <span style={{ fontSize: "13px", color: "var(--muted)" }}>
                            {key.replace(/_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase())}
                          </span>
                          <span style={{ fontWeight: "700" }}>
                            {typeof value === "number" ? value.toFixed(2) : value}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>

                  <PieChart
                    data={costBreakdown}
                    dataKey="value"
                    nameKey="name"
                    title="Cost Breakdown"
                  />
                </div>
              )}

              {!calculateMargin.isSuccess && (
                <div
                  style={{
                    padding: "40px",
                    textAlign: "center",
                    color: "var(--muted)",
                    border: "1px dashed var(--border)",
                    borderRadius: "12px",
                  }}
                >
                  Enter values and click &quot;Calculate Margin&quot; to see results
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Deals Table */}
      <div className="panel" style={{ padding: "18px" }}>
        <div className="h2">Active Lots & Deals</div>
        <div className="muted" style={{ marginBottom: "14px" }}>
          {isLoading ? "Loading deals..." : `${deals.length} lots in system`}
        </div>

        {deals.length > 0 ? (
          <div style={{ overflowX: "auto" }}>
            <table className="table">
              <thead>
                <tr>
                  <th>Reference</th>
                  <th>Origin</th>
                  <th>Variety</th>
                  <th>Process</th>
                  <th>Grade</th>
                  <th>Weight (kg)</th>
                  <th>Cupping Score</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {deals.map((lot) => (
                  <tr key={lot.id}>
                    <td style={{ fontWeight: "600" }}>{(lot as any).reference || `LOT-${lot.id}`}</td>
                    <td>{(lot as any).origin || "–"}</td>
                    <td>{(lot as any).variety || "–"}</td>
                    <td>{(lot as any).process || "–"}</td>
                    <td>{(lot as any).grade || "–"}</td>
                    <td>{(lot as any).weight_kg?.toLocaleString() || "–"}</td>
                    <td>
                      {(lot as any).cupping_score ? (
                        <span className="badge badgeOk">{(lot as any).cupping_score}</span>
                      ) : (
                        "–"
                      )}
                    </td>
                    <td>
                      <span className="badge">
                        {(lot as any).status || "active"}
                      </span>
                    </td>
                    <td>
                      <Link href={`/lots/${lot.id}`} className="link">
                        View →
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="empty" style={{ padding: "40px", textAlign: "center", color: "var(--muted)" }}>
            No deals or lots found. Create a lot to start tracking deals and margins.
          </div>
        )}
      </div>
    </div>
  );
}
