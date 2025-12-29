"use client";

import { useState } from "react";
import Link from "next/link";
import { useRoasters } from "../hooks/useRoasters";
import { RoasterFilters } from "../types";
import { format } from "date-fns";

export default function GermanSalesDashboard() {
  const [filters, setFilters] = useState<RoasterFilters>({
    country: "Germany",
  });

  const { data: roastersData, isLoading } = useRoasters({ ...filters, limit: 100 });
  const roasters = roastersData?.items || [];

  // Calculate pipeline stats
  const stats = {
    total: roasters.length,
    contacted: roasters.filter((r) => r.contact_status === "contacted" || r.contact_status === "in_conversation").length,
    qualified: roasters.filter((r) => r.contact_status === "qualified" || r.contact_status === "proposal").length,
    avgSalesScore: roasters.length > 0
      ? roasters.reduce((sum, r) => sum + (r.sales_fit_score || 0), 0) / roasters.length
      : 0,
  };

  // Priority roasters (high score, not yet contacted or needs followup)
  const priorityRoasters = roasters
    .filter((r) => (r.sales_fit_score || 0) >= 70)
    .sort((a, b) => (b.sales_fit_score || 0) - (a.sales_fit_score || 0))
    .slice(0, 10);

  // Pending followups (roasters with past followup dates)
  const pendingFollowups = roasters.filter((r) => {
    if (!r.next_followup_date) return false;
    const followupDate = new Date(r.next_followup_date);
    return followupDate <= new Date();
  });

  return (
    <div className="page">
      <div className="pageHeader">
        <div>
          <div className="h1">German Roasters Sales Pipeline</div>
          <div className="muted">
            Manage relationships and sales opportunities with German specialty roasters
          </div>
        </div>
        <div className="actions">
          <button className="btn btnPrimary" onClick={() => window.location.reload()}>
            Refresh
          </button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid gridCols4" style={{ marginBottom: "18px" }}>
        <div className="panel card">
          <div className="cardLabel">Total Roasters</div>
          <div className="cardValue">{stats.total}</div>
          <div className="cardHint">In CRM database</div>
        </div>
        <div className="panel card">
          <div className="cardLabel">In Pipeline</div>
          <div className="cardValue">{stats.contacted}</div>
          <div className="cardHint">Contacted or in conversation</div>
        </div>
        <div className="panel card">
          <div className="cardLabel">Qualified</div>
          <div className="cardValue">{stats.qualified}</div>
          <div className="cardHint">Ready for proposals</div>
        </div>
        <div className="panel card">
          <div className="cardLabel">Avg Sales Score</div>
          <div className="cardValue">{stats.avgSalesScore.toFixed(1)}</div>
          <div className="cardHint">Out of 100</div>
        </div>
      </div>

      <div className="grid gridCols2" style={{ marginBottom: "18px" }}>
        {/* Priority Contact List */}
        <div className="panel" style={{ padding: "18px" }}>
          <div className="h2">Priority Contacts</div>
          <div className="muted" style={{ marginBottom: "14px" }}>
            Top 10 roasters by sales fit score
          </div>
          {priorityRoasters.length > 0 ? (
            <div className="list">
              {priorityRoasters.map((roaster) => (
                <div key={roaster.id} className="listRow">
                  <div className="listMain">
                    <div className="listTitle">{roaster.company_name}</div>
                    <div className="listMeta">
                      <span>{roaster.city || "Germany"}</span>
                      {roaster.roaster_type && (
                        <>
                          <span className="dot">•</span>
                          <span>{roaster.roaster_type}</span>
                        </>
                      )}
                    </div>
                  </div>
                  <span
                    className="badge"
                    style={{
                      background: "rgba(87,134,255,0.12)",
                      borderColor: "rgba(87,134,255,0.35)",
                    }}
                  >
                    Score: {roaster.sales_fit_score}
                  </span>
                  <Link href={`/roasters/${roaster.id}`} className="link">
                    View →
                  </Link>
                </div>
              ))}
            </div>
          ) : (
            <div className="empty">No priority contacts found</div>
          )}
        </div>

        {/* Pending Followups */}
        <div className="panel" style={{ padding: "18px" }}>
          <div className="h2">Pending Followups</div>
          <div className="muted" style={{ marginBottom: "14px" }}>
            Roasters requiring followup today or overdue
          </div>
          {pendingFollowups.length > 0 ? (
            <div className="list">
              {pendingFollowups.slice(0, 10).map((roaster) => (
                <div key={roaster.id} className="listRow">
                  <div className="listMain">
                    <div className="listTitle">{roaster.company_name}</div>
                    <div className="listMeta">
                      <span>{roaster.city || "Germany"}</span>
                      {roaster.next_followup_date && (
                        <>
                          <span className="dot">•</span>
                          <span>Due: {format(new Date(roaster.next_followup_date), "MMM dd")}</span>
                        </>
                      )}
                    </div>
                  </div>
                  <span className="badge badgeWarn">Followup</span>
                  <Link href={`/roasters/${roaster.id}`} className="link">
                    Action →
                  </Link>
                </div>
              ))}
            </div>
          ) : (
            <div className="empty">All caught up! No pending followups.</div>
          )}
        </div>
      </div>

      {/* Filters */}
      <div className="panel" style={{ padding: "18px", marginBottom: "18px" }}>
        <div className="h2">Filter Roasters</div>
        <div className="grid gridCols4" style={{ marginTop: "14px", gap: "10px" }}>
          <div>
            <label style={{ fontSize: "12px", color: "var(--muted)", display: "block", marginBottom: "6px" }}>
              City
            </label>
            <input
              type="text"
              className="input"
              placeholder="e.g., Berlin"
              value={filters.city || ""}
              onChange={(e) =>
                setFilters({ ...filters, city: e.target.value || undefined })
              }
            />
          </div>
          <div>
            <label style={{ fontSize: "12px", color: "var(--muted)", display: "block", marginBottom: "6px" }}>
              Roaster Type
            </label>
            <select
              className="input"
              value={filters.roaster_type || ""}
              onChange={(e) =>
                setFilters({ ...filters, roaster_type: e.target.value || undefined })
              }
            >
              <option value="">All Types</option>
              <option value="Specialty">Specialty</option>
              <option value="Commercial">Commercial</option>
              <option value="Micro">Micro</option>
            </select>
          </div>
          <div>
            <label style={{ fontSize: "12px", color: "var(--muted)", display: "block", marginBottom: "6px" }}>
              Min Sales Score
            </label>
            <input
              type="number"
              className="input"
              placeholder="0-100"
              min="0"
              max="100"
              value={filters.min_sales_fit_score || ""}
              onChange={(e) =>
                setFilters({
                  ...filters,
                  min_sales_fit_score: e.target.value ? Number(e.target.value) : undefined,
                })
              }
            />
          </div>
          <div style={{ display: "flex", alignItems: "flex-end" }}>
            <button
              className="btn"
              onClick={() => setFilters({ country: "Germany" })}
              style={{ width: "100%" }}
            >
              Clear Filters
            </button>
          </div>
        </div>
      </div>

      {/* Roasters Table */}
      <div className="panel" style={{ padding: "18px" }}>
        <div className="h2">All Roasters</div>
        <div className="muted" style={{ marginBottom: "14px" }}>
          {isLoading ? "Loading roasters..." : `${roasters.length} roasters found`}
        </div>

        {roasters.length > 0 ? (
          <div style={{ overflowX: "auto" }}>
            <table className="table">
              <thead>
                <tr>
                  <th>Company</th>
                  <th>City</th>
                  <th>Type</th>
                  <th>Capacity (kg)</th>
                  <th>Sales Score</th>
                  <th>Contact Status</th>
                  <th>Last Contact</th>
                  <th>Next Followup</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {roasters.map((roaster) => (
                  <tr key={roaster.id}>
                    <td style={{ fontWeight: "600" }}>{roaster.company_name}</td>
                    <td>{roaster.city || "–"}</td>
                    <td>{roaster.roaster_type || "–"}</td>
                    <td>{roaster.annual_capacity_kg?.toLocaleString() || "–"}</td>
                    <td>
                      {roaster.sales_fit_score ? (
                        <span
                          className="badge"
                          style={{
                            background:
                              roaster.sales_fit_score >= 80
                                ? "rgba(64,214,123,0.12)"
                                : roaster.sales_fit_score >= 60
                                ? "rgba(255,183,64,0.12)"
                                : "rgba(255,92,92,0.12)",
                            borderColor:
                              roaster.sales_fit_score >= 80
                                ? "rgba(64,214,123,0.35)"
                                : roaster.sales_fit_score >= 60
                                ? "rgba(255,183,64,0.35)"
                                : "rgba(255,92,92,0.35)",
                          }}
                        >
                          {roaster.sales_fit_score}
                        </span>
                      ) : (
                        "–"
                      )}
                    </td>
                    <td>
                      {roaster.contact_status ? (
                        <span className="badge">{roaster.contact_status}</span>
                      ) : (
                        <span className="badge">new</span>
                      )}
                    </td>
                    <td>
                      {roaster.last_contact_date
                        ? format(new Date(roaster.last_contact_date), "MMM dd, yyyy")
                        : "–"}
                    </td>
                    <td>
                      {roaster.next_followup_date ? (
                        <span
                          className={
                            new Date(roaster.next_followup_date) <= new Date()
                              ? "badge badgeErr"
                              : "badge"
                          }
                        >
                          {format(new Date(roaster.next_followup_date), "MMM dd")}
                        </span>
                      ) : (
                        "–"
                      )}
                    </td>
                    <td>
                      <Link href={`/roasters/${roaster.id}`} className="link">
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
            No roasters found. Run the Discovery Seed in Operations to populate the database.
          </div>
        )}
      </div>
    </div>
  );
}
