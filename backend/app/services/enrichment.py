from __future__ import annotations

import hashlib
import re
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlparse
import ipaddress
import socket

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


def _validate_public_http_url(url: str) -> str:
    """
    Normalize and validate that the URL uses http(s), that the hostname is
    allowed, and that it does not resolve to localhost or private/internal IP
    address ranges. Raises ValueError on failure.
    """
    normalized = _normalize_url(url)
    if not normalized:
        raise ValueError("empty url")

    parsed = urlparse(normalized)
    if parsed.scheme not in {"http", "https"}:
        raise ValueError("unsupported URL scheme")
    if not parsed.hostname:
        raise ValueError("invalid URL: missing host")

    hostname = parsed.hostname.lower()

    # If an allow-list of hosts/domains is configured, enforce it here.
    allowed_hosts = getattr(settings, "ENRICH_ALLOWED_HOSTS", None) or []
    allowed_domains = getattr(settings, "ENRICH_ALLOWED_DOMAINS", None) or []

    if allowed_hosts or allowed_domains:
        host_allowed = False
        if hostname in {h.lower() for h in allowed_hosts}:
            host_allowed = True
        else:
            for domain in allowed_domains:
                d = (domain or "").lower().lstrip(".")
                if d and (hostname == d or hostname.endswith("." + d)):
                    host_allowed = True
                    break
        if not host_allowed:
            raise ValueError("URL host is not allowed")

    # Optionally restrict ports to typical HTTP(S) ports. If no port is given,
    # httpx will use defaults based on the scheme.
    if parsed.port is not None and parsed.port not in (80, 443):
        raise ValueError("unsupported URL port")

    try:
        addrinfo_list = socket.getaddrinfo(parsed.hostname, None)
    except OSError:
        raise ValueError("unable to resolve host")

    for family, _, _, _, sockaddr in addrinfo_list:
        ip_str = None
        if family == socket.AF_INET:
            ip_str = sockaddr[0]
        elif family == socket.AF_INET6:
            ip_str = sockaddr[0]
        if not ip_str:
            continue
        ip = ipaddress.ip_address(ip_str)
        if (
            ip.is_loopback
            or ip.is_private
            or ip.is_link_local
            or ip.is_multicast
            or ip.is_reserved
            or ip.is_unspecified
        ):
            raise ValueError("URL host resolves to a disallowed IP address")

    return normalized


def fetch_text(url: str, timeout_seconds: int = 25) -> tuple[str, dict[str, Any]]:
    # Validate the initial URL before making any request.
    current_url = _validate_public_http_url(url)
    headers = {
        # browser-like UA reduces dumb 403s (not all)
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36 CoffeeStudio/0.3",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "de-DE,de;q=0.9,en;q=0.8",
    }
    max_redirects = 5
    with httpx.Client(
        timeout=timeout_seconds, follow_redirects=False, headers=headers
    ) as client:
        redirects_followed = 0
        while True:
            r = client.get(current_url)
            # If this is not a redirect, stop here.
            if r.status_code not in {301, 302, 303, 307, 308}:
                break

            location = r.headers.get("location")
            if not location:
                break

            # Resolve relative redirects against the current URL.
            try:
                next_url = str(httpx.URL(current_url).join(location))
            except Exception:
                raise ValueError("invalid redirect URL")

            # Validate each redirect target to prevent SSRF via redirects.
            current_url = _validate_public_http_url(next_url)
            redirects_followed += 1
            if redirects_followed > max_redirects:
                raise ValueError("too many redirects")

        r.raise_for_status()
        html = r.text

    # Re-validate the final URL after following redirects to ensure that
    # redirection did not lead to an internal or otherwise disallowed host.
    final_url_str = str(r.url)
    safe_final_url = _validate_public_http_url(final_url_str)

    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    text = _clean_text(soup.get_text(" "))
    meta = {
        "final_url": safe_final_url,
        "status_code": r.status_code,
        "content_type": r.headers.get("content-type"),
        "domain": _domain(safe_final_url),
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
        "Gib NUR valides JSON zurÃ¼ck (kein Markdown). "
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
        # meta["final_url"] has already been validated in fetch_text.
        final_url = meta.get("final_url") or target_url

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
            # Use isinstance checks for proper type narrowing
            if isinstance(entity, Cooperative):
                if extracted.get("region") and not entity.region:
                    entity.region = str(extracted["region"])[:255]
                    updated_fields.append("region")
                if extracted.get("varieties") and not entity.varieties:
                    entity.varieties = str(extracted["varieties"])[:255]
                    updated_fields.append("varieties")
                if extracted.get("certifications") and not entity.certifications:
                    entity.certifications = str(extracted["certifications"])[:255]
                    updated_fields.append("certifications")
            elif isinstance(entity, Roaster):
                if extracted.get("city") and not entity.city:
                    entity.city = str(extracted["city"])[:255]
                    updated_fields.append("city")

            if extracted.get("contact_email") and not entity.contact_email:
                entity.contact_email = str(extracted["contact_email"])[:320]
                updated_fields.append("contact_email")

            if extracted.get("website") and not entity.website:
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
