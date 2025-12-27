"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { apiFetch } from "../../../lib/api";

type Roaster = {
  id: number;
  name: string;
  city?: string | null;
  website?: string | null;
  contact_email?: string | null;
  peru_focus: boolean;
  specialty_focus: boolean;
  price_position?: string | null;
  notes?: string | null;
  status: string;
  next_action?: string | null;
  requested_data?: string | null;
  total_score?: number | null;
  confidence?: number | null;
  last_verified_at?: string | null;
};

export default function RoasterDetailPage() {
  const params = useParams();
  const id = params?.id as string;
  const [item, setItem] = useState<Roaster | null>(null);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    apiFetch<Roaster>(`/roasters/${id}`)
      .then(setItem)
      .catch((e) => setErr(e.message));
  }, [id]);

  if (err) return <div style={{ color: "crimson" }}>{err}</div>;
  if (!item) return <div>Lade…</div>;

  return (
    <div>
      <h1>{item.name}</h1>
      <div><b>Stadt:</b> {item.city || "-"}</div>
      <div><b>Website:</b> {item.website ? <a href={item.website} target="_blank" rel="noreferrer">{item.website}</a> : "-"}</div>
      <div><b>Kontakt:</b> {item.contact_email || "-"}</div>
      <div><b>Peru-Fokus:</b> {item.peru_focus ? "Ja" : "Nein"}</div>
      <div><b>Specialty:</b> {item.specialty_focus ? "Ja" : "Nein"}</div>
      <div><b>Preisposition:</b> {item.price_position || "-"}</div>
      <div><b>Status:</b> {item.status}</div>
      <div><b>Nächster Schritt:</b> {item.next_action || "-"}</div>
      {item.total_score != null && (
        <div><b>Score:</b> {item.total_score} (Conf {item.confidence ?? "-"})</div>
      )}
      {item.notes && (
        <div style={{ marginTop: 12 }}>
          <h3>Notizen</h3>
          <pre style={{ whiteSpace: "pre-wrap" }}>{item.notes}</pre>
        </div>
      )}
      {item.requested_data && (
        <div style={{ marginTop: 12 }}>
          <h3>Requested Data</h3>
          <pre style={{ whiteSpace: "pre-wrap" }}>{item.requested_data}</pre>
        </div>
      )}
    </div>
  );
}
