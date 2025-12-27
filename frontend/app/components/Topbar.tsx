"use client";

import Link from "next/link";
import React from "react";

export default function Topbar({
  authed,
  onLogout,
}: {
  authed: boolean;
  onLogout: () => void;
}) {
  return (
    <div className="topbar">
      <div className="row" style={{ gap: 12 }}>
        <div className="topbarTitle">Command Center</div>
        <div className="pill">Daten • Workflows • Qualität</div>
      </div>
      <div className="topbarRight">
        {authed ? (
          <button className="btn" onClick={onLogout}>Logout</button>
        ) : (
          <Link className="btn btnPrimary" href="/login">Login</Link>
        )}
      </div>
    </div>
  );
}
