"use client";

import Link from "next/link";
import { format, differenceInDays } from "date-fns";
import { useShipments, useActiveShipments } from "../hooks/useShipments";
import { Shipment } from "../types";

export default function ShipmentsDashboard() {
  // Fetch data from real API
  const { data: shipmentsData, isLoading, error } = useShipments();
  const { data: activeShipments, isLoading: isLoadingActive } = useActiveShipments();

  const shipments = shipmentsData?.items || [];
  
  // Calculate progress from dates
  const calculateProgress = (shipment: Shipment): number => {
    if (shipment.status === "arrived" || shipment.actual_arrival) return 100;
    const eta = shipment.estimated_arrival || shipment.eta;
    if (!shipment.departure_date || !eta) return 0;
    
    const departure = new Date(shipment.departure_date).getTime();
    const etaTime = new Date(eta).getTime();
    const now = Date.now();
    
    if (now < departure) return 0;
    if (now >= etaTime) return 100;
    
    const totalDuration = etaTime - departure;
    const elapsed = now - departure;
    return Math.round((elapsed / totalDuration) * 100);
  };

  // Get reference (bill_of_lading or legacy reference)
  const getReference = (shipment: Shipment): string => {
    return shipment.reference || shipment.bill_of_lading || `SHP-${shipment.id}`;
  };

  // Get ETA (estimated_arrival or legacy eta)
  const getEta = (shipment: Shipment): string | null => {
    return shipment.estimated_arrival || shipment.eta || null;
  };

  // Calculate stats
  const stats = {
    total: shipments.length,
    inTransit: shipments.filter((s) => s.status === "in_transit").length,
    arrived: shipments.filter((s) => s.status === "arrived").length,
    totalWeight: shipments.reduce((sum, s) => sum + s.weight_kg, 0),
  };

  // Shipments arriving soon (within 7 days)
  const arrivingSoon = shipments.filter((s) => {
    if (s.status !== "in_transit") return false;
    const eta = getEta(s);
    if (!eta) return false;
    const daysUntilArrival = differenceInDays(new Date(eta), new Date());
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

  // Loading state
  if (isLoading || isLoadingActive) {
    return (
      <div className="page">
        <div className="pageHeader">
          <div>
            <div className="h1">Sendungsverfolgung</div>
            <div className="muted">
              Verfolgen Sie Kaffeesendungen von Peru nach Deutschland und Europa
            </div>
          </div>
        </div>
        <div style={{ padding: "40px", textAlign: "center" }}>
          <div style={{ fontSize: "16px", color: "var(--muted)" }}>Lade Sendungen...</div>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="page">
        <div className="pageHeader">
          <div>
            <div className="h1">Sendungsverfolgung</div>
            <div className="muted">
              Verfolgen Sie Kaffeesendungen von Peru nach Deutschland und Europa
            </div>
          </div>
        </div>
        <div style={{ padding: "40px", textAlign: "center" }}>
          <div style={{ fontSize: "16px", color: "#ff5555", marginBottom: "12px" }}>
            ⚠️ Fehler beim Laden der Sendungen
          </div>
          <div style={{ fontSize: "14px", color: "var(--muted)" }}>
            {error instanceof Error ? error.message : "Unbekannter Fehler"}
          </div>
        </div>
      </div>
    );
  }

  // Empty state
  if (shipments.length === 0) {
    return (
      <div className="page">
        <div className="pageHeader">
          <div>
            <div className="h1">Sendungsverfolgung</div>
            <div className="muted">
              Verfolgen Sie Kaffeesendungen von Peru nach Deutschland und Europa
            </div>
          </div>
          <div className="actions">
            <button type="button" className="btn btnPrimary">Sendung hinzufügen</button>
          </div>
        </div>
        <div style={{ padding: "60px 40px", textAlign: "center" }}>
          <div style={{ fontSize: "48px", marginBottom: "16px" }}>📦</div>
          <div style={{ fontSize: "18px", fontWeight: "600", marginBottom: "8px" }}>
            Keine Sendungen vorhanden
          </div>
          <div style={{ fontSize: "14px", color: "var(--muted)", marginBottom: "20px" }}>
            Erstellen Sie Ihre erste Sendung, um mit dem Tracking zu beginnen
          </div>
          <button type="button" className="btn btnPrimary">Erste Sendung erstellen</button>
        </div>
      </div>
    );
  }

  return (
    <div className="page">
      <div className="pageHeader">
        <div>
          <div className="h1">Sendungsverfolgung</div>
          <div className="muted">
            Verfolgen Sie Kaffeesendungen von Peru nach Deutschland und Europa
          </div>
        </div>
        <div className="actions">
          <button type="button" className="btn btnPrimary">Sendung hinzufügen</button>
        </div>
      </div>

      {/* Overview KPIs */}
      <div className="grid gridCols4" style={{ marginBottom: "18px" }}>
        <div className="panel card">
          <div className="cardLabel">Sendungen gesamt</div>
          <div className="cardValue">{stats.total}</div>
          <div className="cardHint">Alle Zeiten</div>
        </div>
        <div className="panel card">
          <div className="cardLabel">In Transit</div>
          <div className="cardValue">{stats.inTransit}</div>
          <div className="cardHint">Aktuell im Versand</div>
        </div>
        <div className="panel card">
          <div className="cardLabel">Angekommen</div>
          <div className="cardValue">{stats.arrived}</div>
          <div className="cardHint">Abgeschlossene Lieferungen</div>
        </div>
        <div className="panel card">
          <div className="cardLabel">Gesamtgewicht</div>
          <div className="cardValue">{(stats.totalWeight / 1000).toFixed(1)}t</div>
          <div className="cardHint">Kaffee verschifft</div>
        </div>
      </div>

      {/* Arriving Soon Widget */}
      {arrivingSoon.length > 0 && (
        <div className="panel" style={{ padding: "18px", marginBottom: "18px" }}>
          <div className="h2">Bald ankommend</div>
          <div className="muted" style={{ marginBottom: "14px" }}>
            Sendungen, die innerhalb von 7 Tagen ankommen
          </div>
          <div className="grid gridCols3" style={{ gap: "12px" }}>
            {arrivingSoon.map((shipment) => {
              const eta = getEta(shipment);
              const daysUntilArrival = eta ? differenceInDays(new Date(eta), new Date()) : 0;
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
                    {getReference(shipment)}
                  </div>
                  <div style={{ fontSize: "13px", color: "var(--muted)", marginBottom: "8px" }}>
                    {shipment.origin_port} → {shipment.destination_port}
                  </div>
                  <div style={{ fontSize: "20px", fontWeight: "800", marginBottom: "4px" }}>
                    {daysUntilArrival} Tage
                  </div>
                  <div style={{ fontSize: "12px", color: "var(--muted)" }}>
                    ETA: {eta ? format(new Date(eta), "dd. MMM yyyy") : "–"}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Active Shipments Cards */}
      <div className="panel" style={{ padding: "18px", marginBottom: "18px" }}>
        <div className="h2">Aktive Sendungen</div>
        <div className="muted" style={{ marginBottom: "14px" }}>
          Aktuell in Transit
        </div>
        <div className="grid gridCols2" style={{ gap: "14px" }}>
          {shipments
            .filter((s) => s.status === "in_transit")
            .map((shipment) => {
              const statusColors = getStatusColor(shipment.status);
              const progress = calculateProgress(shipment);
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
                        {getReference(shipment)}
                      </div>
                      <div style={{ fontSize: "13px", color: "var(--muted)" }}>
                        {shipment.carrier || shipment.container_type || "–"}
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
                      {shipment.current_location ? `Aktuell: ${shipment.current_location}` : "Position wird ermittelt"}
                    </div>
                  </div>

                  <div style={{ marginBottom: "12px" }}>
                    <div style={{ display: "flex", justifyContent: "space-between", fontSize: "12px", marginBottom: "6px" }}>
                      <span>Fortschritt</span>
                      <span>{progress}%</span>
                    </div>
                    <div style={{ width: "100%", height: "6px", background: "rgba(0,0,0,0.2)", borderRadius: "999px", overflow: "hidden" }}>
                      <div
                        style={{
                          width: `${progress}%`,
                          height: "100%",
                          background: "rgba(200,149,108,0.8)",
                          transition: "width 0.3s ease",
                        }}
                      />
                    </div>
                  </div>

                  <div className="grid gridCols2" style={{ gap: "10px", fontSize: "12px" }}>
                    <div>
                      <div style={{ color: "var(--muted)" }}>Abfahrt</div>
                      <div style={{ fontWeight: "600" }}>
                        {shipment.departure_date ? format(new Date(shipment.departure_date), "dd. MMM") : "–"}
                      </div>
                    </div>
                    <div>
                      <div style={{ color: "var(--muted)" }}>ETA</div>
                      <div style={{ fontWeight: "600" }}>
                        {getEta(shipment) ? format(new Date(getEta(shipment)!), "dd. MMM") : "–"}
                      </div>
                    </div>
                  </div>

                  <div style={{ marginTop: "12px", paddingTop: "12px", borderTop: "1px solid var(--border)" }}>
                    <Link href={`/shipments/${shipment.id}`} className="btn" style={{ width: "100%", fontSize: "12px", display: "block", textAlign: "center", textDecoration: "none" }}>
                      Details anzeigen →
                    </Link>
                  </div>
                </div>
              );
            })}
        </div>
      </div>

      {/* All Shipments Table */}
      <div className="panel" style={{ padding: "18px" }}>
        <div className="h2">Alle Sendungen</div>
        <div className="muted" style={{ marginBottom: "14px" }}>
          Vollständiger Sendungsverlauf
        </div>

        <div style={{ overflowX: "auto" }}>
          <table className="table">
            <thead>
              <tr>
                <th>Referenz</th>
                <th>Route</th>
                <th>Spediteur</th>
                <th>Container</th>
                <th>Gewicht (kg)</th>
                <th>Abfahrt</th>
                <th>ETA / Ankunft</th>
                <th>Status</th>
                <th>Aktionen</th>
              </tr>
            </thead>
            <tbody>
              {shipments.map((shipment) => {
                const statusColors = getStatusColor(shipment.status);
                const eta = getEta(shipment);
                return (
                  <tr key={shipment.id}>
                    <td style={{ fontWeight: "600" }}>{getReference(shipment)}</td>
                    <td>
                      {shipment.origin_port} → {shipment.destination_port}
                    </td>
                    <td>{shipment.carrier || "–"}</td>
                    <td className="mono" style={{ fontSize: "12px" }}>
                      {shipment.container_number}
                    </td>
                    <td>{shipment.weight_kg.toLocaleString()}</td>
                    <td>{shipment.departure_date ? format(new Date(shipment.departure_date), "MMM dd, yyyy") : "–"}</td>
                    <td>
                      {shipment.actual_arrival
                        ? format(new Date(shipment.actual_arrival), "MMM dd, yyyy")
                        : eta
                        ? format(new Date(eta), "MMM dd, yyyy")
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
                      <Link href={`/shipments/${shipment.id}`} className="link">Ansehen →</Link>
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
