"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import React from "react";

const items: { href: string; label: string; badge?: string }[] = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/cooperatives", label: "Peru Sourcing" },
  { href: "/roasters", label: "German Sales" },
  { href: "/lots", label: "Shipments" },
  { href: "/margin-analysis", label: "Margins" },
  { href: "/news", label: "Marktradar" },
  { href: "/reports", label: "Reports" },
  { href: "/ops", label: "Operations" },
];

export default function Sidebar({ authed }: { authed: boolean }) {
  const pathname = usePathname();
  const [collapsed, setCollapsed] = React.useState(false);

  return (
    <aside className={"sidebar " + (collapsed ? "collapsed" : "")}> 
      <div className="brand">
        <div className="logo">CS</div>
        {!collapsed && (
          <div>
            <div className="brandTitle">CoffeeStudio</div>
            <div className="brandSub">Option D • MAXSTACK</div>
          </div>
        )}
      </div>

      <button className="ghost" onClick={() => setCollapsed((v) => !v)}>
        {collapsed ? "»" : "«"}
      </button>

      <nav className="nav">
        {items.map((it) => {
          const active = pathname === it.href || (it.href !== "/" && pathname?.startsWith(it.href + "/"));
          return (
            <Link key={it.href} href={authed ? it.href : "/login"} className={"navItem " + (active ? "active" : "")}> 
              <span>{it.label}</span>
            </Link>
          );
        })}
      </nav>

      <div className="sidebarFooter">
        {!collapsed && (
          <div className="muted small">
            Tipp: Öffne <span className="mono">http://traefik.localhost/dashboard/</span> für Routing-Checks.
          </div>
        )}
      </div>
    </aside>
  );
}
