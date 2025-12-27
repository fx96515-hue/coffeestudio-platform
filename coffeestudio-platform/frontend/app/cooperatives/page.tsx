"use client";

import { useEffect, useState } from "react";
import { apiFetch } from "../../lib/api";
import Link from "next/link";

type Coop = { id: number; name: string; region?: string | null; total_score?: number | null; confidence?: number | null };

export default function CooperativesPage() {
  const [items, setItems] = useState<Coop[]>([]);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    apiFetch<Coop[]>("/cooperatives")
      .then(setItems)
      .catch((e) => setErr(e.message));
  }, []);

  return (
    <div>
      <h1>Kooperativen</h1>
      {err && <div style={{ color: "crimson" }}>{err}</div>}
      <ul>
        {items.map((c) => (
          <li key={c.id}>
            <Link href={`/cooperatives/${c.id}`}>{c.name}</Link>
            {c.region ? ` — ${c.region}` : ""}
          </li>
        ))}
      </ul>
    </div>
  );
}
