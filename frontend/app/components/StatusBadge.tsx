import Badge from "./Badge";

export type Status = 
  | "active" 
  | "pending" 
  | "completed" 
  | "failed" 
  | "in_progress" 
  | "shipped"
  | "delivered"
  | "open"
  | "closed"
  | "won"
  | "lost";

const statusMap: Record<Status, { tone: "good" | "warn" | "bad" | "neutral"; label?: string }> = {
  active: { tone: "good" },
  pending: { tone: "warn" },
  completed: { tone: "good" },
  failed: { tone: "bad" },
  in_progress: { tone: "warn", label: "In Progress" },
  shipped: { tone: "good" },
  delivered: { tone: "good" },
  open: { tone: "neutral" },
  closed: { tone: "neutral" },
  won: { tone: "good" },
  lost: { tone: "bad" },
};

export default function StatusBadge({ status }: { status: Status | string }) {
  const config = statusMap[status as Status] || { tone: "neutral" as const };
  const label = config.label || status.replace(/_/g, " ");
  
  return <Badge tone={config.tone}>{label}</Badge>;
}
