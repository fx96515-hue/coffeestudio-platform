"use client";

import { useEffect, useState } from "react";
import { apiFetch } from "../../lib/api";
import Link from "next/link";

type Me = { id: number; email: string; role: string; is_active: boolean };

export default function DashboardPage() {
  const [me, setMe] = useState<Me | null>(null);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    apiFetch<Me>("/auth/me")
      .then(setMe)
      .catch((e) => setErr(e.message));
  }, []);

  return (
    <div>
      <h1>Dashboard</h1>
      {err && <div style={{ color: "crimson" }}>{err}</div>}
      {me ? (
        <div>
          <div><b>User:</b> {me.email} ({me.role})</div>
          <ul>
            <li><Link href="/cooperatives">Kooperativen</Link></li>
            <li><Link href="/roasters">Röster</Link></li>
            <li><Link href="/lots">Lots</Link></li>
            <li><Link href="/reports">Reports</Link></li>
          </ul>
        </div>
      ) : (
        <div>Loading…</div>
      )}
    </div>
  );
}
