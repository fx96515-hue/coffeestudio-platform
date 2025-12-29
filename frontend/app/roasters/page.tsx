"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { apiFetch } from "../../lib/api";
import Badge from "../components/Badge";

type Roaster = {
  id: number;
  name: string;
  country?: string | null;
  city?: string | null;
  website?: string | null;
};

type RoasterList = { items: Roaster[]; total: number };

export default function RoastersPage() {
  const [data, setData] = useState<RoasterList | null>(null);
  const [q, setQ] = useState("");
  const [cityFilter, setCityFilter] = useState("");
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    (async () => {
      try {
        const d = await apiFetch<RoasterList>("/roasters?limit=200");
        setData(d);
      } catch (e: any) {
        setErr(e?.message ?? String(e));
      }
    })();
  }, []);

  const filtered = useMemo(() => {
    const items = data?.items ?? [];
    const t = q.trim().toLowerCase();
    let result = items;
    
    if (t) {
      result = result.filter((r) => `${r.name} ${r.city ?? ""} ${r.country ?? ""}`.toLowerCase().includes(t));
    }
    
    if (cityFilter) {
      result = result.filter((r) => r.city === cityFilter);
    }
    
    return result;
  }, [data, q, cityFilter]);

  const cities = useMemo(() => {
    const items = data?.items ?? [];
    const uniqueCities = new Set(items.map(r => r.city).filter((c): c is string => Boolean(c)));
    return Array.from(uniqueCities).sort();
  }, [data]);

  return (
    <div className="page">
      <div className="pageHeader">
        <div>
          <div className="h1">German Sales Pipeline</div>
          <div className="muted">Roasters, communications, and sales opportunities</div>
        </div>
        <div className="row gap">
          <select
            className="input"
            value={cityFilter}
            onChange={(e) => setCityFilter(e.target.value)}
            style={{ width: 180 }}
          >
            <option value="">All Cities</option>
            {cities.map(c => (
              <option key={c} value={c}>{c}</option>
            ))}
          </select>
          <input 
            className="input" 
            style={{ width: 280 }} 
            placeholder="Search roasters..." 
            value={q} 
            onChange={(e) => setQ(e.target.value)} 
          />
          <Link className="btn" href="/ops">
            Discovery
          </Link>
        </div>
      </div>

      {err ? <div className="error">{err}</div> : null}

      <div className="panel">
        <div style={{ padding: 16, borderBottom: "1px solid var(--border)" }}>
          <div className="panelTitle">
            Roasters: <span className="mono">{filtered.length}</span> (total {data?.total ?? "–"})
          </div>
        </div>
        <div className="tableWrap">
          <table className="table">
            <thead>
              <tr>
                <th style={{ width: 80 }}>ID</th>
                <th>Name</th>
                <th>City</th>
                <th>Country</th>
                <th>Website</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((r) => (
                <tr key={r.id}>
                  <td className="mono">{r.id}</td>
                  <td>
                    <Link className="link" href={`/roasters/${r.id}`}>
                      {r.name}
                    </Link>
                  </td>
                  <td>{r.city ?? "–"}</td>
                  <td>{r.country ?? "–"}</td>
                  <td>
                    {r.website ? (
                      <a className="link" href={r.website.startsWith("http") ? r.website : `https://${r.website}`} target="_blank" rel="noreferrer">
                        <Badge tone="good">Website</Badge>
                      </a>
                    ) : (
                      <Badge tone="warn">Missing</Badge>
                    )}
                  </td>
                  <td>
                    <Badge>Lead</Badge>
                  </td>
                  <td>
                    <Link className="link" href={`/roasters/${r.id}`} style={{ fontSize: 12 }}>
                      View Details →
                    </Link>
                  </td>
                </tr>
              ))}
              {!filtered.length ? (
                <tr>
                  <td colSpan={7} className="muted" style={{ padding: 16 }}>
                    No roasters found.
                  </td>
                </tr>
              ) : null}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
