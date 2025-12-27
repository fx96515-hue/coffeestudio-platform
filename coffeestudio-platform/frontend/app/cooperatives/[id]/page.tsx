"use client";

import { useEffect, useState } from "react";
import { apiFetch } from "../../../lib/api";

type Coop = {
  id: number;
  name: string;
  region?: string | null;
  certifications?: string | null;
  contact_email?: string | null;
  website?: string | null;
  notes?: string | null;
  total_score?: number | null;
  confidence?: number | null;
};

export default function CoopDetail({ params }: { params: { id: string } }) {
  const [item, setItem] = useState<Coop | null>(null);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    apiFetch<Coop>(`/cooperatives/${params.id}`)
      .then(setItem)
      .catch((e) => setErr(e.message));
  }, [params.id]);

  if (err) return <div style={{ color: "crimson" }}>{err}</div>;
  if (!item) return <div>Loading…</div>;

  return (
    <div>
      <h1>{item.name}</h1>
      <div><b>Region:</b> {item.region || "-"}</div>
      <div><b>Zertifizierungen:</b> {item.certifications || "-"}</div>
      <div><b>Kontakt:</b> {item.contact_email || "-"}</div>
      <div><b>Website:</b> {item.website || "-"}</div>
      <div><b>Score:</b> {item.total_score ?? "-"} / <b>Confidence:</b> {item.confidence ?? "-"}</div>
      <h3>Notizen</h3>
      <pre style={{ whiteSpace: "pre-wrap" }}>{item.notes || "-"}</pre>
    </div>
  );
}
