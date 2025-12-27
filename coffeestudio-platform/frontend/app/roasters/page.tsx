"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { apiFetch } from "../../lib/api";

type Roaster = {
  id: number;
  name: string;
  city?: string | null;
  website?: string | null;
  contact_email?: string | null;
  peru_focus: boolean;
  specialty_focus: boolean;
  price_position?: string | null;
};

export default function RoastersPage() {
  const [items, setItems] = useState<Roaster[]>([]);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    apiFetch<Roaster[]>("/roasters")
      .then(setItems)
      .catch((e) => setErr(e.message));
  }, []);

  return (
    <div>
      <h1>Röster</h1>
      {err && <div style={{ color: "crimson" }}>{err}</div>}
      <ul>
        {items.map((r) => (
          <li key={r.id}>
            <Link href={`/roasters/${r.id}`}>{r.name}</Link>
            {r.city ? ` — ${r.city}` : ""} {r.peru_focus ? " (Peru)" : ""}
          </li>
        ))}
      </ul>
    </div>
  );
}
