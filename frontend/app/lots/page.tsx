import { useEffect, useState, useMemo } from "react";
import Link from "next/link";
import { apiFetch } from "../../lib/api";
import Badge from "../components/Badge";

type Lot = {
  id: number;
  cooperative_id: number;
  name: string;
  crop_year?: number | null;
  incoterm?: string | null;
  price_per_kg?: number | null;
  currency?: string | null;
  weight_kg?: number | null;
  expected_cupping_score?: number | null;
};

type LotForm = {
  cooperative_id: string;
  name: string;
  crop_year: string;
  incoterm: string;
  price_per_kg: string;
  currency: string;
  weight_kg: string;
  expected_cupping_score: string;
};

export default function LotsPage() {
  const [lots, setLots] = useState<Lot[]>([]);
  const [err, setErr] = useState<string | null>(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [statusFilter, setStatusFilter] = useState("");
  const [form, setForm] = useState<LotForm>({
    cooperative_id: "",
    name: "",
    crop_year: "",
    incoterm: "FOB",
    price_per_kg: "",
    currency: "USD",
    weight_kg: "",
    expected_cupping_score: "",
  });

  const load = () =>
    apiFetch<Lot[]>("/lots?limit=200")
      .then(setLots)
      .catch((e) => setErr(e.message));

  useEffect(() => {
    load();
  }, []);

  async function createLot() {
    setErr(null);
    setIsSubmitting(true);
    try {
      const payload: Partial<Lot> = {
        cooperative_id: Number(form.cooperative_id),
        name: String(form.name || "").trim(),
        incoterm: form.incoterm || null,
        currency: form.currency || null,
      };
      if (!payload.name) throw new Error("Name fehlt");
      if (!payload.cooperative_id) throw new Error("cooperative_id fehlt");

      if (form.crop_year) payload.crop_year = Number(form.crop_year);
      if (form.price_per_kg) payload.price_per_kg = Number(form.price_per_kg);
      if (form.weight_kg) payload.weight_kg = Number(form.weight_kg);
      if (form.expected_cupping_score) payload.expected_cupping_score = Number(form.expected_cupping_score);

      await apiFetch<Lot>("/lots", { method: "POST", body: JSON.stringify(payload) });
      setForm({ cooperative_id: "", name: "", crop_year: "", incoterm: "FOB", price_per_kg: "", currency: "USD", weight_kg: "", expected_cupping_score: "" });
      setShowCreateForm(false);
      load();
    } catch (e: any) {
      setErr(e.message);
    } finally {
      setIsSubmitting(false);
    }
  }

  const filteredLots = useMemo(() => {
    if (!statusFilter) return lots;
    // Note: Lots don't have status in the current schema, so this is placeholder
    // In a real implementation, you'd filter based on actual status field
    return lots;
  }, [lots, statusFilter]);

  return (
    <div className="page">
      <div className="pageHeader">
        <div>
          <div className="h1">Shipment Tracking</div>
          <div className="muted">Track coffee lots from origin to destination</div>
        </div>
        <div className="row gap">
          <select
            className="input"
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            style={{ width: 180 }}
          >
            <option value="">All Status</option>
            <option value="pending">Pending</option>
            <option value="in_transit">In Transit</option>
            <option value="delivered">Delivered</option>
          </select>
          <button className="btn btnPrimary" onClick={() => setShowCreateForm(!showCreateForm)}>
            {showCreateForm ? "Cancel" : "+ New Lot"}
          </button>
        </div>
      </div>

      {err && <div style={{ color: "crimson", marginBottom: 16 }}>{err}</div>}

      {showCreateForm && (
        <div className="panel" style={{ padding: 18, marginBottom: 18 }}>
          <div className="panelTitle" style={{ marginBottom: 12 }}>Create New Lot</div>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: 12, marginTop: 12 }}>
          <div>
            <label htmlFor="cooperative-id" className="muted" style={{ fontSize: 12, display: "block", marginBottom: 4 }}>Cooperative ID</label>
            <input id="cooperative-id" className="input" placeholder="cooperative_id" value={form.cooperative_id} onChange={(e) => setForm({ ...form, cooperative_id: e.target.value })} />
          </div>
          <div>
            <label htmlFor="lot-name" className="muted" style={{ fontSize: 12, display: "block", marginBottom: 4 }}>Lot Name</label>
            <input id="lot-name" className="input" placeholder="Name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
          </div>
          <div>
            <label htmlFor="crop-year" className="muted" style={{ fontSize: 12, display: "block", marginBottom: 4 }}>Crop Year</label>
            <input id="crop-year" className="input" placeholder="2024" value={form.crop_year} onChange={(e) => setForm({ ...form, crop_year: e.target.value })} />
          </div>
          <div>
            <label htmlFor="incoterm" className="muted" style={{ fontSize: 12, display: "block", marginBottom: 4 }}>Incoterm</label>
            <input id="incoterm" className="input" placeholder="FOB/CIF" value={form.incoterm} onChange={(e) => setForm({ ...form, incoterm: e.target.value })} />
          </div>
          <div>
            <label htmlFor="price-per-kg" className="muted" style={{ fontSize: 12, display: "block", marginBottom: 4 }}>Price/kg</label>
            <input id="price-per-kg" className="input" placeholder="5.50" value={form.price_per_kg} onChange={(e) => setForm({ ...form, price_per_kg: e.target.value })} />
          </div>
          <div>
            <label htmlFor="currency" className="muted" style={{ fontSize: 12, display: "block", marginBottom: 4 }}>Currency</label>
            <input id="currency" className="input" placeholder="USD" value={form.currency} onChange={(e) => setForm({ ...form, currency: e.target.value })} />
          </div>
          <div>
            <label htmlFor="weight-kg" className="muted" style={{ fontSize: 12, display: "block", marginBottom: 4 }}>Weight (kg)</label>
            <input id="weight-kg" className="input" placeholder="18000" value={form.weight_kg} onChange={(e) => setForm({ ...form, weight_kg: e.target.value })} />
          </div>
          <div>
            <label htmlFor="expected-sca" className="muted" style={{ fontSize: 12, display: "block", marginBottom: 4 }}>Expected SCA Score</label>
            <input id="expected-sca" className="input" placeholder="84" value={form.expected_cupping_score} onChange={(e) => setForm({ ...form, expected_cupping_score: e.target.value })} />
          </div>
        </div>
        <button
          onClick={createLot}
          disabled={isSubmitting}
          className="btn btnPrimary"
          style={{ marginTop: 12 }}
        >
          {isSubmitting ? "Creating..." : "Create Lot"}
        </button>
        <div className="muted" style={{ fontSize: 12, marginTop: 8 }}>
          Note: Get cooperative_id from the Peru Sourcing page.
        </div>
      </div>
      )}

      <div className="panel">
        <div style={{ padding: 16, borderBottom: "1px solid var(--border)" }}>
          <div className="panelTitle">Coffee Lots</div>
        </div>
        
        {filteredLots.length === 0 ? (
          <div className="empty" style={{ padding: 32 }}>
            No lots available. Create your first lot to start tracking shipments.
          </div>
        ) : (
          <div className="tableWrap">
            <table className="table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Name</th>
                  <th>Cooperative</th>
                  <th>Crop Year</th>
                  <th>Weight</th>
                  <th>Price</th>
                  <th>SCA Score</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredLots.map((l) => (
                  <tr key={l.id}>
                    <td className="mono">{l.id}</td>
                    <td>
                      <Link className="link" href={`/lots/${l.id}`}>
                        {l.name}
                      </Link>
                    </td>
                    <td className="muted">#{l.cooperative_id}</td>
                    <td className="muted">{l.crop_year ?? "–"}</td>
                    <td>{l.weight_kg ? `${l.weight_kg} kg` : "–"}</td>
                    <td>
                      {l.price_per_kg != null ? (
                        <Badge>{l.price_per_kg} {l.currency || "USD"}/kg</Badge>
                      ) : "–"}
                    </td>
                    <td>
                      {l.expected_cupping_score ? (
                        <Badge tone="good">{l.expected_cupping_score}</Badge>
                      ) : "–"}
                    </td>
                    <td>
                      <Link className="link" href={`/lots/${l.id}`} style={{ fontSize: 12 }}>
                        Track →
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
