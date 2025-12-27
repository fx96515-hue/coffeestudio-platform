from __future__ import annotations

import hashlib
import re
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.config import settings
from app.models.cooperative import Cooperative
from app.models.roaster import Roaster
from app.models.web_extract import WebExtract
from app.models.entity_event import EntityEvent
from app.providers.perplexity import PerplexityClient, safe_json_loads


def _clean_text(txt: str) -> str:
    return re.sub(r"\s+", " ", txt or "").strip()


def _sha256(text: str) -> str:
    return hashlib.sha256((text or "").encode("utf-8", errors="ignore")).hexdigest()


def _domain(url: str) -> str | None:
    try:
        return urlparse(url).netloc.lower() or None
    except Exception:
        return None


def _normalize_url(u: str) -> str:
    u = (u or "").strip()
    if not u:
        return u
    if not re.match(r"^https?://", u, flags=re.I):
        u = "https://" + u.lstrip("/")
    return u


def fetch_text(url: str, timeout_seconds: int = 25) -> tuple[str, dict[str, Any]]:
    headers = {
        # browser-like UA reduces dumb 403s (not all)
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36 CoffeeStudio/0.3",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "de-DE,de;q=0.9,en;q=0.8",
    }
    with httpx.Client(
        timeout=timeout_seconds, follow_redirects=True, headers=headers
    ) as client:
        r = client.get(url)
        r.raise_for_status()
        html = r.text

    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    text = _clean_text(soup.get_text(" "))
    meta = {
        "final_url": str(r.url),
        "status_code": r.status_code,
        "content_type": r.headers.get("content-type"),
        "domain": _domain(str(r.url)),
    }
    return text[:20000], meta


def _extract_structured_with_llm(
    client: PerplexityClient, *, entity_type: str, text: str
) -> dict[str, Any]:
    schema = {
        "type": "object",
        "properties": {
            "region": {"type": ["string", "null"]},
            "city": {"type": ["string", "null"]},
            "varieties": {"type": ["string", "null"]},
            "processing": {"type": ["string", "null"]},
            "certifications": {"type": ["string", "null"]},
            "export_ready": {"type": ["boolean", "null"]},
            "contact_email": {"type": ["string", "null"]},
            "website": {"type": ["string", "null"]},
            "summary_de": {"type": ["string", "null"]},
        },
        "required": [],
        "additionalProperties": False,
    }
    system = (
        "Du extrahierst strukturierte Kaffee-Entity-Infos aus einem Webseiten-Text. "
        "Gib NUR valides JSON zurück (kein Markdown). "
        "Nichts erfinden. Unbekannt => null. "
        f"Entity-Typ: {entity_type}. "
        "Wenn der Text nicht passt: alles null."
    )
    content = client.chat_completions(
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": text[:12000]},
        ],
        temperature=0.0,
        max_tokens=900,
        response_format={"type": "json_schema", "json_schema": {"schema": schema}},
    )
    data = safe_json_loads(content)
    return data if isinstance(data, dict) else {}


def enrich_entity(
    db: Session,
    *,
    entity_type: str,
    entity_id: int,
    url: str | None = None,
    use_llm: bool = True,
) -> dict[str, Any]:
    if entity_type not in {"cooperative", "roaster"}:
        raise ValueError("entity_type must be cooperative|roaster")

    entity = (
        db.get(Cooperative, entity_id)
        if entity_type == "cooperative"
        else db.get(Roaster, entity_id)
    )
    if not entity:
        raise ValueError("entity not found")

    target_url = _normalize_url(url or getattr(entity, "website", None) or "")
    if not target_url:
        raise ValueError("no url (provide url or set entity.website)")

    now = datetime.now(timezone.utc)

    try:
        text, meta = fetch_text(target_url)
        chash = _sha256(text)
        final_url = _normalize_url(meta.get("final_url") or target_url)

        # IMPORTANT: stmt must be a SQLAlchemy select(), never a plain string
        stmt = select(WebExtract).where(
            WebExtract.entity_type == entity_type,
            WebExtract.entity_id == entity_id,
            WebExtract.url == final_url,
        )
        we = db.scalar(stmt)

        if not we:
            we = WebExtract(entity_type=entity_type, entity_id=entity_id, url=final_url)
            db.add(we)

        we.status = "ok"
        we.retrieved_at = now
        we.content_text = text
        we.content_hash = chash
        we.meta = meta

        extracted: dict[str, Any] = {}
        if use_llm and settings.PERPLEXITY_API_KEY:
            client = PerplexityClient()
            try:
                extracted = _extract_structured_with_llm(
                    client, entity_type=entity_type, text=text
                )
            finally:
                client.close()

        we.extracted_json = extracted or None
        db.commit()
        db.refresh(we)

        updated_fields: list[str] = []
        if extracted:
            if entity_type == "cooperative":
                if extracted.get("region") and not getattr(entity, "region", None):
                    entity.region = str(extracted["region"])[:255]
                    updated_fields.append("region")
                if extracted.get("varieties") and not getattr(
                    entity, "varieties", None
                ):
                    entity.varieties = str(extracted["varieties"])[:255]
                    updated_fields.append("varieties")
                if extracted.get("certifications") and not getattr(
                    entity, "certifications", None
                ):
                    entity.certifications = str(extracted["certifications"])[:255]
                    updated_fields.append("certifications")
            else:
                if extracted.get("city") and not getattr(entity, "city", None):
                    entity.city = str(extracted["city"])[:255]
                    updated_fields.append("city")

            if extracted.get("contact_email") and not getattr(
                entity, "contact_email", None
            ):
                entity.contact_email = str(extracted["contact_email"])[:320]
                updated_fields.append("contact_email")

            if extracted.get("website") and not getattr(entity, "website", None):
                entity.website = _normalize_url(str(extracted["website"]))[:500]
                updated_fields.append("website")

            entity.last_verified_at = now
            updated_fields.append("last_verified_at")
            db.add(entity)

        db.add(
            EntityEvent(
                entity_type=entity_type,
                entity_id=entity_id,
                event_type="enriched",
                payload={"url": target_url, "updated_fields": updated_fields},
            )
        )
        db.commit()

        return {
            "status": "ok",
            "entity_type": entity_type,
            "entity_id": entity_id,
            "url": target_url,
            "web_extract_id": we.id,
            "updated_fields": updated_fields,
            "used_llm": bool(use_llm and settings.PERPLEXITY_API_KEY),
        }

    except Exception as e:
        we = WebExtract(
            entity_type=entity_type,
            entity_id=entity_id,
            url=target_url,
            status="failed",
            retrieved_at=now,
            meta={"error": str(e)},
        )
        db.add(we)
        db.add(
            EntityEvent(
                entity_type=entity_type,
                entity_id=entity_id,
                event_type="enrich_failed",
                payload={"url": target_url, "error": str(e)},
            )
        )
        db.commit()
        return {
            "status": "failed",
            "error": str(e),
            "entity_type": entity_type,
            "entity_id": entity_id,
            "url": target_url,
        }
