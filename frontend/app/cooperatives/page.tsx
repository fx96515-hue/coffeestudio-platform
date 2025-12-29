"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { apiFetch } from "../../lib/api";
import Badge from "../components/Badge";

type Coop = {
  id: number;
  name: string;
  region?: string | null;
  country?: string | null;
  website?: string | null;
  sca_score?: number | null;
};

type CoopList = { items: Coop[]; total: number };

export default function CooperativesPage() {
  const [data, setData] = useState<CoopList | null>(null);
  const [q, setQ] = useState("");
  const [regionFilter, setRegionFilter] = useState("");
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    (async () => {
      try {
        const res = await apiFetch<CoopList>(`/cooperatives?limit=200`);
        setData(res);
      } catch (e: any) {
        setErr(e?.message ?? String(e));
      }
    })();
  }, []);

  const rows = useMemo(() => {
    const items = data?.items ?? [];
    const searchQuery = q.trim().toLowerCase();
    let filtered = items;
    
    if (searchQuery) {
      filtered = filtered.filter((c) =>
        [c.name, c.region ?? "", c.country ?? "", c.website ?? ""].join(" ").toLowerCase().includes(searchQuery),
      );
    }
    
    if (regionFilter) {
      filtered = filtered.filter((c) => c.region === regionFilter);
    }
    
    return filtered;
  }, [data, q, regionFilter]);

  const regions = useMemo(() => {
    const items = data?.items ?? [];
    const uniqueRegions = new Set(items.map(c => c.region).filter((r): r is string => Boolean(r)));
    return Array.from(uniqueRegions).sort();
  }, [data]);

  return (
    <div className="page">
      <div className="pageHeader">
        <div>
          <div className="h1">Peru Sourcing Intelligence</div>
          <div className="muted">Cooperatives, regions, and sourcing analysis</div>
        </div>
        <div className="row gap">
          <select
            className="input"
            value={regionFilter}
            onChange={(e) => setRegionFilter(e.target.value)}
            style={{ width: 180 }}
          >
            <option value="">All Regions</option>
            {regions.map(r => (
              <option key={r} value={r}>{r}</option>
            ))}
          </select>
          <input
            className="input"
            placeholder="Search cooperatives..."
            value={q}
            onChange={(e) => setQ(e.target.value)}
            style={{ width: 280 }}
          />
          <Link className="btn" href="/ops">
            Enrichment
          </Link>
        </div>
      </div>

      {err ? <div className="error">{err}</div> : null}

      <div className="panel">
        <div style={{ padding: 16, borderBottom: "1px solid var(--border)" }}>
          <div className="panelTitle">
            Cooperatives: {rows.length} {data ? <span className="muted">(total {data.total})</span> : null}
          </div>
        </div>

        <div className="tableWrap">
          <table className="table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Region</th>
                <th>Country</th>
                <th>Website</th>
                <th>Quality Score</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((c) => (
                <tr key={c.id}>
                  <td>
                    <Link className="link" href={`/cooperatives/${c.id}`}>
                      {c.name}
                    </Link>
                  </td>
                  <td className="muted">{c.region ?? "–"}</td>
                  <td className="muted">{c.country ?? "–"}</td>
                  <td>
                    {c.website ? (
                      <a className="link" href={(c.website.startsWith("http") ? c.website : `https://${c.website}`)} target="_blank" rel="noreferrer">
                        {c.website}
                      </a>
                    ) : (
                      <Badge tone="warn">fehlend</Badge>
                    )}
                  </td>
                  <td>{c.sca_score ? <Badge tone="good">{c.sca_score}</Badge> : <Badge>–</Badge>}</td>
                  <td>
                    <Link className="link" href={`/cooperatives/${c.id}`} style={{ fontSize: 12 }}>
                      View Details →
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
