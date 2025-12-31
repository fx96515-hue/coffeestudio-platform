from __future__ import annotations

import json
import re
from datetime import datetime
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.cooperative import Cooperative
from app.models.evidence import EntityEvidence
from app.models.roaster import Roaster
from app.models.source import Source
from app.providers.perplexity import PerplexityClient, PerplexityError, safe_json_loads


def _entities_response_format() -> dict[str, Any]:
    schema: dict[str, Any] = {
        "type": "object",
        "properties": {
            "entities": {
                "type": "array",
                "maxItems": 20,
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "country": {"type": ["string", "null"]},
                        "region": {"type": ["string", "null"]},
                        "website": {"type": ["string", "null"]},
                        "contact_email": {"type": ["string", "null"]},
                        "notes": {"type": ["string", "null"]},
                        "evidence_urls": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["name", "evidence_urls"],
                    "additionalProperties": False,
                },
            }
        },
        "required": ["entities"],
        "additionalProperties": False,
    }
    return {"type": "json_schema", "json_schema": {"schema": schema}}


def _repair_json_with_llm(client: PerplexityClient, raw: str) -> dict[str, Any]:
    system = (
        "Du bist ein JSON-Repair-Bot. Du bekommst fehlerhaften JSON-Text und gibst NUR valides JSON zurück. "
        "Keine Erklärungen, kein Markdown. Verwende doppelte Anführungszeichen. "
        "Wenn Inhalte fehlen oder abgeschnitten sind, entferne die kaputten Teile statt zu raten. "
        "Output MUSS strikt parsebar sein und genau ein JSON-Objekt enthalten."
    )
    content = client.chat_completions(
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": raw[:12000]},
        ],
        temperature=0.0,
        max_tokens=1800,
        response_format=_entities_response_format(),
    )
    data = safe_json_loads(content)
    if not isinstance(data, dict):
        raise ValueError("JSON repair returned non-object")
    return data


def _norm_name(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", name.strip().lower())


def _get_or_create_source(
    db: Session,
    name: str,
    url: str | None,
    kind: str = "api",
    reliability: float | None = 0.6,
) -> Source:
    stmt = select(Source).where(func.lower(Source.name) == name.lower())
    src = db.scalar(stmt)
    if src:
        return src
    src = Source(name=name, url=url, kind=kind, reliability=reliability)
    db.add(src)
    db.commit()
    db.refresh(src)
    return src


COOP_QUERIES = [
    "Peru coffee cooperative exporter list",
    "cooperativa cafetalera peru exportadora",
    "cooperativa cafe peru fairtrade organic",
    "central de cooperativas café Perú exportación",
    "Peru coffee cooperative Cajamarca",
    "Peru coffee cooperative Junin Satipo",
    "Peru coffee cooperative Puno Sandia",
]

ROASTER_QUERIES = [
    "specialty coffee roaster Germany",
    "Kaffeerösterei Deutschland specialty direct trade",
    "Third Wave coffee roastery Deutschland",
    "Rösterei Berlin specialty coffee",
    "Rösterei München specialty coffee",
    "Rösterei Hamburg specialty coffee",
]


def _extract_entities_with_llm(
    client: PerplexityClient,
    *,
    entity_type: str,
    search_results: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    system = (
        "Du extrahierst strukturierte Entitäten aus Suchergebnissen. "
        "Gib NUR valides JSON zurück (kein Markdown, keine Erklärungen). "
        "Gib GENAU ein JSON-Objekt zurück mit dem Feld 'entities'. "
        'Schema: {"entities":[{"name":string,"country":string|null,"region":string|null,'
        '"website":string|null,"contact_email":string|null,"notes":string|null,'
        '"evidence_urls":[string]}]} '
        f"Regeln: (1) nichts erfinden; unbekannt => null/[]; (2) nur echte {entity_type}; "
        "(3) Duplikate entfernen; (4) evidence_urls nur aus gelieferten URLs; (5) max 20 entities."
    )

    user = {"entity_type": entity_type, "results": search_results}
    content = client.chat_completions(
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": json.dumps(user, ensure_ascii=False)},
        ],
        temperature=0.0,
        max_tokens=2200,
        response_format=_entities_response_format(),
    )
    try:
        data = safe_json_loads(content)
    except Exception:
        data = _repair_json_with_llm(client, content)

    ents = data.get("entities") or []
    if not isinstance(ents, list):
        return []

    cleaned: list[dict[str, Any]] = []
    for ent in ents:
        if not isinstance(ent, dict):
            continue
        name = (ent.get("name") or "").strip()
        if not name:
            continue
        evidence_urls = ent.get("evidence_urls") or []
        if not isinstance(evidence_urls, list):
            evidence_urls = []
        cleaned.append(
            {
                "name": name,
                "country": ent.get("country"),
                "region": ent.get("region"),
                "website": ent.get("website"),
                "contact_email": ent.get("contact_email"),
                "notes": ent.get("notes"),
                "evidence_urls": [u for u in evidence_urls if isinstance(u, str)],
            }
        )

    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    for ent in cleaned:
        k = _norm_name(ent["name"])
        if k in seen:
            continue
        seen.add(k)
        out.append(ent)
    return out


def seed_discovery(
    db: Session,
    *,
    entity_type: str,
    max_entities: int = 200,
    dry_run: bool = False,
    country_filter: str | None = None,
) -> dict[str, Any]:
    if entity_type not in {"cooperative", "roaster"}:
        raise ValueError("entity_type must be cooperative|roaster")

    src = _get_or_create_source(
        db,
        name="Perplexity Discovery",
        url="https://docs.perplexity.ai/",
        kind="api",
        reliability=0.6,
    )

    queries = COOP_QUERIES if entity_type == "cooperative" else ROASTER_QUERIES
    default_country = "PE" if entity_type == "cooperative" else "DE"
    country = country_filter or default_country

    created = 0
    updated = 0
    skipped = 0
    errors: list[str] = []

    client = PerplexityClient()
    try:
        aggregated: list[dict[str, Any]] = []
        seen_urls: set[str] = set()

        for q in queries:
            if len(aggregated) >= 120:
                break
            try:
                results = client.search(
                    q, max_results=20, country=country, max_tokens_per_page=512
                )
                for r in results:
                    if r.url in seen_urls:
                        continue
                    seen_urls.add(r.url)
                    aggregated.append(
                        {"title": r.title, "url": r.url, "snippet": r.snippet}
                    )
            except Exception as exc:
                errors.append(f"search failed for '{q}': {exc}")

        entities: list[dict[str, Any]] = []
        chunk_size = 20
        for i in range(0, len(aggregated), chunk_size):
            chunk = aggregated[i : i + chunk_size]
            if not chunk:
                continue
            try:
                ents = _extract_entities_with_llm(
                    client, entity_type=entity_type, search_results=chunk
                )
                entities.extend(ents)
            except Exception as exc:
                errors.append(f"extract failed chunk {i}-{i + chunk_size}: {exc}")

        deduped: dict[str, dict[str, Any]] = {}
        for ent in entities:
            k = _norm_name(ent["name"])
            if not k:
                continue
            if k not in deduped:
                deduped[k] = ent
            else:
                deduped[k]["evidence_urls"] = list(
                    {
                        *(deduped[k].get("evidence_urls") or []),
                        *(ent.get("evidence_urls") or []),
                    }
                )

        now = datetime.utcnow()

        for ent in list(deduped.values())[:max_entities]:
            name = ent["name"].strip()
            entity_id: int | None = None

            if entity_type == "cooperative":
                stmt_coop = select(Cooperative).where(
                    func.lower(Cooperative.name) == name.lower()
                )
                coop = db.scalar(stmt_coop)
                is_new = coop is None
                if coop is None:
                    coop = Cooperative(
                        name=name, status="active", next_action="In Recherche"
                    )
                    db.add(coop)

                if ent.get("region") and not coop.region:
                    coop.region = str(ent["region"])[:255]
                if ent.get("website") and not coop.website:
                    coop.website = str(ent["website"])[:500]
                if ent.get("contact_email") and not coop.contact_email:
                    coop.contact_email = str(ent["contact_email"])[:320]
                if ent.get("notes"):
                    coop.notes = (coop.notes or "").strip()
                    add = str(ent["notes"]).strip()
                    if add and add not in (coop.notes or ""):
                        coop.notes = (
                            (coop.notes + "\n\n" + add).strip() if coop.notes else add
                        )

                coop.meta = coop.meta or {}
                coop.meta.setdefault("discovery", {})
                coop.meta["discovery"].update(
                    {"provider": "perplexity", "last_run": now.isoformat()}
                )

                if not dry_run:
                    db.commit()
                    db.refresh(coop)
                    entity_id = coop.id

            else:
                stmt_roaster = select(Roaster).where(
                    func.lower(Roaster.name) == name.lower()
                )
                roaster = db.scalar(stmt_roaster)
                is_new = roaster is None
                if roaster is None:
                    roaster = Roaster(
                        name=name, status="active", next_action="In Recherche"
                    )
                    db.add(roaster)

                if ent.get("region") and not roaster.city:
                    roaster.city = str(ent["region"])[:255]
                if ent.get("website") and not roaster.website:
                    roaster.website = str(ent["website"])[:500]
                if ent.get("contact_email") and not roaster.contact_email:
                    roaster.contact_email = str(ent["contact_email"])[:320]
                if ent.get("notes"):
                    roaster.notes = (roaster.notes or "").strip()
                    add = str(ent["notes"]).strip()
                    if add and add not in (roaster.notes or ""):
                        roaster.notes = (
                            (roaster.notes + "\n\n" + add).strip()
                            if roaster.notes
                            else add
                        )

                roaster.meta = roaster.meta or {}
                roaster.meta.setdefault("discovery", {})
                roaster.meta["discovery"].update(
                    {"provider": "perplexity", "last_run": now.isoformat()}
                )

                if not dry_run:
                    db.commit()
                    db.refresh(roaster)
                    entity_id = roaster.id

            ev_urls = list(dict.fromkeys((ent.get("evidence_urls") or [])))

            if ev_urls and (not dry_run) and entity_id is not None:
                for u in ev_urls[:10]:
                    try:
                        ev = EntityEvidence(
                            entity_type=entity_type,
                            entity_id=entity_id,
                            source_id=src.id,
                            evidence_url=u,
                            extracted_at=now,
                            meta={"provider": "perplexity"},
                        )
                        db.add(ev)
                        db.commit()
                    except Exception:
                        db.rollback()

            if is_new:
                created += 1
            else:
                updated += 1

        if dry_run:
            db.rollback()

    except PerplexityError as exc:
        errors.append(str(exc))
    finally:
        client.close()

    return {
        "entity_type": entity_type,
        "country": country,
        "dry_run": dry_run,
        "created": created,
        "updated": updated,
        "skipped": skipped,
        "errors": errors,
    }
