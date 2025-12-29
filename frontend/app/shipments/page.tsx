"use client";

import { useState } from "react";
import { format, differenceInDays } from "date-fns";

export default function ShipmentsDashboard() {
  // Helper function to format date for API (YYYY-MM-DD)
  const formatDate = (date: Date) => date.toISOString().split("T")[0];
  
  const today = new Date();
  
  // Shipment 1: departed 15 days ago, arrives in 20 days
  const shipment1Departure = new Date(today);
  shipment1Departure.setDate(today.getDate() - 15);
  const shipment1Eta = new Date(today);
  shipment1Eta.setDate(today.getDate() + 20);
  
  // Shipment 2: departed 10 days ago, arrives in 25 days
  const shipment2Departure = new Date(today);
  shipment2Departure.setDate(today.getDate() - 10);
  const shipment2Eta = new Date(today);
  shipment2Eta.setDate(today.getDate() + 25);
  
  // Shipment 3: departed 60 days ago, arrived 55 days ago (completed)
  const shipment3Departure = new Date(today);
  shipment3Departure.setDate(today.getDate() - 60);
  const shipment3Eta = new Date(today);
  shipment3Eta.setDate(today.getDate() - 55);
  const shipment3Arrival = new Date(today);
  shipment3Arrival.setDate(today.getDate() - 55);
  
  // Mock shipments data - in real implementation, this would come from an API
  const mockShipments = [
    {
      id: 1,
      reference: "SHP-2024-001",
      origin_port: "Callao, Peru",
      destination_port: "Hamburg, Germany",
      departure_date: formatDate(shipment1Departure),
      eta: formatDate(shipment1Eta),
      status: "in_transit",
      carrier: "Maersk Line",
      container_number: "MSCU1234567",
      weight_kg: 18000,
      current_location: "Pacific Ocean",
      progress: 65,
    },
    {
      id: 2,
      reference: "SHP-2024-002",
      origin_port: "Callao, Peru",
      destination_port: "Rotterdam, Netherlands",
      departure_date: formatDate(shipment2Departure),
      eta: formatDate(shipment2Eta),
      status: "in_transit",
      carrier: "MSC",
      container_number: "MSCU7654321",
      weight_kg: 20000,
      current_location: "Panama Canal",
      progress: 45,
    },
    {
      id: 3,
      reference: "SHP-2024-003",
      origin_port: "Callao, Peru",
      destination_port: "Hamburg, Germany",
      departure_date: formatDate(shipment3Departure),
      eta: formatDate(shipment3Eta),
      actual_arrival: formatDate(shipment3Arrival),
      status: "arrived",
      carrier: "Hapag-Lloyd",
      container_number: "HLCU9876543",
      weight_kg: 19000,
      current_location: "Hamburg Port",
      progress: 100,
    },
  ];

  const [shipments] = useState(mockShipments);

  // Calculate stats
  const stats = {
    total: shipments.length,
    inTransit: shipments.filter((s) => s.status === "in_transit").length,
    arrived: shipments.filter((s) => s.status === "arrived").length,
    totalWeight: shipments.reduce((sum, s) => sum + s.weight_kg, 0),
  };

  // Shipments arriving soon (within 7 days)
  const arrivingSoon = shipments.filter((s) => {
    if (s.status !== "in_transit" || !s.eta) return false;
    const daysUntilArrival = differenceInDays(new Date(s.eta), new Date());
    return daysUntilArrival >= 0 && daysUntilArrival <= 7;
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case "in_transit":
        return { bg: "rgba(87,134,255,0.12)", border: "rgba(87,134,255,0.35)" };
      case "arrived":
        return { bg: "rgba(64,214,123,0.12)", border: "rgba(64,214,123,0.35)" };
      case "delayed":
        return { bg: "rgba(255,183,64,0.12)", border: "rgba(255,183,64,0.35)" };
      default:
        return { bg: "rgba(255,255,255,0.02)", border: "var(--border)" };
    }
  };

  return (
    <div className="page">
      <div className="pageHeader">
        <div>
          <div className="h1">Shipments Tracking</div>
          <div className="muted">
            Track coffee shipments from Peru to Germany and Europe
          </div>
        </div>
        <div className="actions">
          <button type="button" className="btn btnPrimary">Add Shipment</button>
        </div>
      </div>

      {/* Overview KPIs */}
      <div className="grid gridCols4" style={{ marginBottom: "18px" }}>
        <div className="panel card">
          <div className="cardLabel">Total Shipments</div>
          <div className="cardValue">{stats.total}</div>
          <div className="cardHint">All time</div>
        </div>
        <div className="panel card">
          <div className="cardLabel">In Transit</div>
          <div className="cardValue">{stats.inTransit}</div>
          <div className="cardHint">Currently shipping</div>
        </div>
        <div className="panel card">
          <div className="cardLabel">Arrived</div>
          <div className="cardValue">{stats.arrived}</div>
          <div className="cardHint">Completed deliveries</div>
        </div>
        <div className="panel card">
          <div className="cardLabel">Total Weight</div>
          <div className="cardValue">{(stats.totalWeight / 1000).toFixed(1)}t</div>
          <div className="cardHint">Coffee shipped</div>
        </div>
      </div>

      {/* Arriving Soon Widget */}
      {arrivingSoon.length > 0 && (
        <div className="panel" style={{ padding: "18px", marginBottom: "18px" }}>
          <div className="h2">Arriving Soon</div>
          <div className="muted" style={{ marginBottom: "14px" }}>
            Shipments arriving within 7 days
          </div>
          <div className="grid gridCols3" style={{ gap: "12px" }}>
            {arrivingSoon.map((shipment) => {
              const daysUntilArrival = differenceInDays(new Date(shipment.eta!), new Date());
              return (
                <div
                  key={shipment.id}
                  className="panel"
                  style={{
                    padding: "14px",
                    background: "rgba(255,183,64,0.08)",
                    border: "1px solid rgba(255,183,64,0.25)",
                  }}
                >
                  <div style={{ fontWeight: "700", marginBottom: "6px" }}>
                    {shipment.reference}
                  </div>
                  <div style={{ fontSize: "13px", color: "var(--muted)", marginBottom: "8px" }}>
                    {shipment.origin_port} → {shipment.destination_port}
                  </div>
                  <div style={{ fontSize: "20px", fontWeight: "800", marginBottom: "4px" }}>
                    {daysUntilArrival} days
                  </div>
                  <div style={{ fontSize: "12px", color: "var(--muted)" }}>
                    ETA: {format(new Date(shipment.eta!), "MMM dd, yyyy")}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Active Shipments Cards */}
      <div className="panel" style={{ padding: "18px", marginBottom: "18px" }}>
        <div className="h2">Active Shipments</div>
        <div className="muted" style={{ marginBottom: "14px" }}>
          Currently in transit
        </div>
        <div className="grid gridCols2" style={{ gap: "14px" }}>
          {shipments
            .filter((s) => s.status === "in_transit")
            .map((shipment) => {
              const statusColors = getStatusColor(shipment.status);
              return (
                <div
                  key={shipment.id}
                  className="panel"
                  style={{
                    padding: "18px",
                    background: statusColors.bg,
                    border: `1px solid ${statusColors.border}`,
                  }}
                >
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "start", marginBottom: "12px" }}>
                    <div>
                      <div style={{ fontWeight: "700", fontSize: "16px", marginBottom: "4px" }}>
                        {shipment.reference}
                      </div>
                      <div style={{ fontSize: "13px", color: "var(--muted)" }}>
                        {shipment.carrier}
                      </div>
                    </div>
                    <span className="badge" style={{ background: statusColors.bg, borderColor: statusColors.border }}>
                      {shipment.status.replace("_", " ")}
                    </span>
                  </div>

                  <div style={{ marginBottom: "12px" }}>
                    <div style={{ fontSize: "14px", marginBottom: "4px" }}>
                      <strong>Route:</strong> {shipment.origin_port} → {shipment.destination_port}
                    </div>
                    <div style={{ fontSize: "13px", color: "var(--muted)" }}>
                      Current: {shipment.current_location}
                    </div>
                  </div>

                  <div style={{ marginBottom: "12px" }}>
                    <div style={{ display: "flex", justifyContent: "space-between", fontSize: "12px", marginBottom: "6px" }}>
                      <span>Progress</span>
                      <span>{Math.min(100, Math.max(0, shipment.progress))}%</span>
                    </div>
                    <div style={{ width: "100%", height: "6px", background: "rgba(0,0,0,0.2)", borderRadius: "999px", overflow: "hidden" }}>
                      <div
                        style={{
                          width: `${Math.min(100, Math.max(0, shipment.progress))}%`,
                          height: "100%",
                          background: "rgba(87,134,255,0.8)",
                          transition: "width 0.3s ease",
                        }}
                      />
                    </div>
                  </div>

                  <div className="grid gridCols2" style={{ gap: "10px", fontSize: "12px" }}>
                    <div>
                      <div style={{ color: "var(--muted)" }}>Departure</div>
                      <div style={{ fontWeight: "600" }}>
                        {format(new Date(shipment.departure_date), "MMM dd")}
                      </div>
                    </div>
                    <div>
                      <div style={{ color: "var(--muted)" }}>ETA</div>
                      <div style={{ fontWeight: "600" }}>
                        {shipment.eta ? format(new Date(shipment.eta), "MMM dd") : "–"}
                      </div>
                    </div>
                  </div>

                  <div style={{ marginTop: "12px", paddingTop: "12px", borderTop: "1px solid var(--border)" }}>
                    <button type="button" className="btn" style={{ width: "100%", fontSize: "12px" }}>
                      View Details →
                    </button>
                  </div>
                </div>
              );
            })}
        </div>
      </div>

      {/* All Shipments Table */}
      <div className="panel" style={{ padding: "18px" }}>
        <div className="h2">All Shipments</div>
        <div className="muted" style={{ marginBottom: "14px" }}>
          Complete shipment history
        </div>

        <div style={{ overflowX: "auto" }}>
          <table className="table">
            <thead>
              <tr>
                <th>Reference</th>
                <th>Route</th>
                <th>Carrier</th>
                <th>Container</th>
                <th>Weight (kg)</th>
                <th>Departure</th>
                <th>ETA / Arrival</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {shipments.map((shipment) => {
                const statusColors = getStatusColor(shipment.status);
                return (
                  <tr key={shipment.id}>
                    <td style={{ fontWeight: "600" }}>{shipment.reference}</td>
                    <td>
                      {shipment.origin_port} → {shipment.destination_port}
                    </td>
                    <td>{shipment.carrier}</td>
                    <td className="mono" style={{ fontSize: "12px" }}>
                      {shipment.container_number}
                    </td>
                    <td>{shipment.weight_kg.toLocaleString()}</td>
                    <td>{format(new Date(shipment.departure_date), "MMM dd, yyyy")}</td>
                    <td>
                      {shipment.actual_arrival
                        ? format(new Date(shipment.actual_arrival), "MMM dd, yyyy")
                        : shipment.eta
                        ? format(new Date(shipment.eta), "MMM dd, yyyy")
                        : "–"}
                    </td>
                    <td>
                      <span
                        className="badge"
                        style={{
                          background: statusColors.bg,
                          borderColor: statusColors.border,
                        }}
                      >
                        {shipment.status.replace("_", " ")}
                      </span>
                    </td>
                    <td>
                      <button className="link">View →</button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
