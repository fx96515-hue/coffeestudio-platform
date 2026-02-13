"use client";

import { useEffect, useState } from "react";
import { apiFetch } from "../../lib/api";

interface MarketPoint {
  value: number;
  unit?: string | null;
  currency?: string | null;
  observed_at: string;
}

interface MarketSnapshot {
  [key: string]: MarketPoint | null;
}

export default function MarketPriceWidget() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [market, setMarket] = useState<MarketSnapshot | null>(null);

  useEffect(() => {
    let alive = true;
    (async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await apiFetch<MarketSnapshot>("/market/latest");
        if (!alive) return;
        setMarket(data);
      } catch (e: unknown) {
        if (!alive) return;
        setError(e instanceof Error ? e.message : String(e));
      } finally {
        if (!alive) return;
        setLoading(false);
      }
    })();

    return () => {
      alive = false;
    };
  }, []);

  const coffeePrice = market?.["COFFEE_C:USD_LB"] ?? null;
  const eurUsd = market?.["EUR_USD"] ?? null;

  // Fallback reference prices
  const fallbackCoffeePrice = 3.50; // USD/lb

  const formatDate = (dateStr?: string | null) => {
    if (!dateStr) return "–";
    const d = new Date(dateStr);
    return d.toLocaleString("de-DE", { dateStyle: "short", timeStyle: "short" });
  };

  return (
    <div className="panel card">
      <div className="cardLabel">Kaffeebörsenpreis</div>
      
      {error ? (
        <div style={{ fontSize: "12px", color: "var(--bad)", marginTop: "8px" }}>
          Fehler beim Laden
        </div>
      ) : loading ? (
        <div className="cardValue">…</div>
      ) : (
        <>
          <div className="cardValue">
            {coffeePrice 
              ? `$${coffeePrice.value.toFixed(2)}/lb` 
              : `$${fallbackCoffeePrice.toFixed(2)}/lb`}
          </div>
          <div className="cardHint">
            {coffeePrice 
              ? `Coffee C · ${formatDate(coffeePrice.observed_at)}` 
              : "Coffee C · Referenzwert"}
          </div>
          
          {eurUsd && (
            <div style={{ fontSize: "12px", color: "var(--muted)", marginTop: "8px" }}>
              EUR/USD: {eurUsd.value.toFixed(4)}
            </div>
          )}
          
          {!coffeePrice && (
            <div style={{ fontSize: "11px", color: "var(--muted)", marginTop: "8px", fontStyle: "italic" }}>
              Keine Live-Daten · Referenzwert: ${fallbackCoffeePrice}/lb
            </div>
          )}
        </>
      )}
    </div>
  );
}
