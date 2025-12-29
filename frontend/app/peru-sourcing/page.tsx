"use client";

import { useState } from "react";
import Link from "next/link";
import { usePeruRegions, useCooperatives } from "../hooks/usePeruRegions";
import { CooperativeFilters } from "../types";

export default function PeruSourcingDashboard() {
  const [filters, setFilters] = useState<CooperativeFilters>({});
  const [selectedCoopId, setSelectedCoopId] = useState<number | null>(null);

  const { data: regions, isLoading: regionsLoading } = usePeruRegions();
  const { data: coopsData, isLoading: coopsLoading } = useCooperatives({ ...filters, limit: 50 });

  const cooperatives = coopsData?.items || [];

  return (
    <div className="page">
      <div className="pageHeader">
        <div>
          <div className="h1">Peru Sourcing Intelligence</div>
          <div className="muted">
            Discover coffee regions, cooperatives, and sourcing opportunities in Peru
          </div>
        </div>
        <div className="actions">
          <button className="btn btnPrimary" onClick={() => window.location.reload()}>
            Refresh
          </button>
        </div>
      </div>

      {/* Peru Regions Overview */}
      <div className="panel" style={{ padding: "18px", marginBottom: "18px" }}>
        <div className="h2">Peru Coffee Regions</div>
        <div className="muted" style={{ marginBottom: "14px" }}>
          {regionsLoading ? "Loading regions..." : `${regions?.length || 0} coffee-growing regions`}
        </div>
        <div className="grid gridCols4">
          {regions?.map((region) => (
            <div
              key={region.id}
              className="panel"
              style={{ padding: "14px", background: "rgba(255,255,255,0.02)" }}
            >
              <div style={{ fontWeight: "700", marginBottom: "6px" }}>{region.name}</div>
              <div className="muted" style={{ fontSize: "13px", marginBottom: "8px" }}>
                {region.description_de || "Peru coffee region"}
              </div>
              {region.altitude_range && (
                <div className="badge" style={{ marginTop: "6px" }}>
                  {region.altitude_range}
                </div>
              )}
              {region.typical_varieties && (
                <div style={{ fontSize: "12px", marginTop: "6px", color: "var(--muted)" }}>
                  Varieties: {region.typical_varieties}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Filters Section */}
      <div className="panel" style={{ padding: "18px", marginBottom: "18px" }}>
        <div className="h2">Filter Cooperatives</div>
        <div className="grid gridCols4" style={{ marginTop: "14px", gap: "10px" }}>
          <div>
            <label style={{ fontSize: "12px", color: "var(--muted)", display: "block", marginBottom: "6px" }}>
              Region
            </label>
            <select
              className="input"
              value={filters.region || ""}
              onChange={(e) =>
                setFilters({ ...filters, region: e.target.value || undefined })
              }
            >
              <option value="">All Regions</option>
              {regions?.map((r) => (
                <option key={r.id} value={r.name}>
                  {r.name}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label style={{ fontSize: "12px", color: "var(--muted)", display: "block", marginBottom: "6px" }}>
              Min Capacity (kg)
            </label>
            <input
              type="number"
              className="input"
              placeholder="e.g., 10000"
              value={filters.min_capacity || ""}
              onChange={(e) =>
                setFilters({
                  ...filters,
                  min_capacity: e.target.value ? Number(e.target.value) : undefined,
                })
              }
            />
          </div>
          <div>
            <label style={{ fontSize: "12px", color: "var(--muted)", display: "block", marginBottom: "6px" }}>
              Min Score
            </label>
            <input
              type="number"
              className="input"
              placeholder="0-100"
              min="0"
              max="100"
              value={filters.min_score || ""}
              onChange={(e) =>
                setFilters({
                  ...filters,
                  min_score: e.target.value ? Number(e.target.value) : undefined,
                })
              }
            />
          </div>
          <div style={{ display: "flex", alignItems: "flex-end" }}>
            <button
              className="btn"
              onClick={() => setFilters({})}
              style={{ width: "100%" }}
            >
              Clear Filters
            </button>
          </div>
        </div>
      </div>

      {/* Cooperatives Table */}
      <div className="panel" style={{ padding: "18px" }}>
        <div className="h2">Cooperatives Directory</div>
        <div className="muted" style={{ marginBottom: "14px" }}>
          {coopsLoading
            ? "Loading cooperatives..."
            : `${cooperatives.length} cooperatives found`}
        </div>

        {cooperatives.length > 0 ? (
          <div style={{ overflowX: "auto" }}>
            <table className="table">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Region</th>
                  <th>Members</th>
                  <th>Capacity (kg)</th>
                  <th>Certifications</th>
                  <th>Quality Score</th>
                  <th>Contact</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {cooperatives.map((coop) => (
                  <tr key={coop.id}>
                    <td style={{ fontWeight: "600" }}>{coop.name}</td>
                    <td>{coop.region || "–"}</td>
                    <td>{coop.members_count?.toLocaleString() || "–"}</td>
                    <td>{coop.annual_production_kg?.toLocaleString() || "–"}</td>
                    <td>
                      {coop.certifications?.length > 0 ? (
                        <div style={{ display: "flex", gap: "4px", flexWrap: "wrap" }}>
                          {coop.certifications.slice(0, 2).map((cert, i) => (
                            <span key={i} className="badge">
                              {cert}
                            </span>
                          ))}
                          {coop.certifications.length > 2 && (
                            <span className="badge">+{coop.certifications.length - 2}</span>
                          )}
                        </div>
                      ) : (
                        "–"
                      )}
                    </td>
                    <td>
                      {coop.quality_score ? (
                        <span
                          className="badge"
                          style={{
                            background:
                              coop.quality_score >= 80
                                ? "rgba(64,214,123,0.12)"
                                : coop.quality_score >= 60
                                ? "rgba(255,183,64,0.12)"
                                : "rgba(255,92,92,0.12)",
                            borderColor:
                              coop.quality_score >= 80
                                ? "rgba(64,214,123,0.35)"
                                : coop.quality_score >= 60
                                ? "rgba(255,183,64,0.35)"
                                : "rgba(255,92,92,0.35)",
                          }}
                        >
                          {coop.quality_score}
                        </span>
                      ) : (
                        "–"
                      )}
                    </td>
                    <td>
                      {coop.contact_email || coop.contact_phone ? (
                        <span className="badge badgeOk">Yes</span>
                      ) : (
                        <span className="badge">No</span>
                      )}
                    </td>
                    <td>
                      <Link href={`/cooperatives/${coop.id}`} className="link">
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
            No cooperatives found. Try adjusting your filters or run the Discovery Seed in Operations.
          </div>
        )}
      </div>
    </div>
  );
}
