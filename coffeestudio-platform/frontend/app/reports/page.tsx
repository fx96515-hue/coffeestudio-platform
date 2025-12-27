"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { apiFetch } from "../../lib/api";

type Report = {
  id: number;
  kind: string;
  title?: string | null;
  report_at: string;
};

export default function ReportsPage() {
  const [reports, setReports] = useState<Report[]>([]);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    apiFetch<Report[]>("/reports?limit=50")
      .then(setReports)
      .catch((e) => setErr(e.message));
  }, []);

  return (
    <div>
      <h1>Reports</h1>
      {err && <div style={{ color: "crimson" }}>{err}</div>}

      <div style={{ marginBottom: 12, color: "#444" }}>
        Generierte Tagesreports (aus DB). Neueste oben.
      </div>

      {reports.length === 0 ? (
        <div>Keine Reports vorhanden.</div>
      ) : (
        <ul>
          {reports.map((r) => (
            <li key={r.id} style={{ marginBottom: 8 }}>
              <Link href={`/reports/${r.id}`}>
                {r.title || `Report #${r.id}`}
              </Link>
              <div style={{ fontSize: 12, color: "#555" }}>
                {new Date(r.report_at).toLocaleString()} — {r.kind}
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
