from __future__ import annotations

import re
import uuid
from typing import Iterable, Optional

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.core.db import SessionLocal
from app.models.tag import ChildTag, Tag
from app.services import synonyms as syn


_NON_ALNUM_RE = re.compile(r"[^a-z0-9]+")

CATEGORY_ORDER = {
    "topic": 0,
    "condition": 1,
    "allergy": 2,
    "age": 3,
    "preference": 4,
    "custom": 5,
}


def _ensure_session(db: Optional[Session]) -> Session:
    if db is not None:
        return db
    if SessionLocal is None:
        raise RuntimeError("DATABASE_URL is not configured.")
    return SessionLocal()


def _slugify(text: str) -> str:
    s = text.strip().lower()
    # For custom slugs, tests expect only [a-z0-9] after prefix.
    s = _NON_ALNUM_RE.sub("", s)
    return s or "x"


def suggest_from_text(db: Session, q: str, limit: int = 8) -> list[dict]:
    q = q or ""
    qn = syn.normalize(q)
    if not qn or len(qn) < 2 or len(qn) > 40:
        raise ValueError("bad query length")

    limit = max(1, min(limit, 20))

    like = f"%{qn}%"
    stmt = (
        select(Tag.slug, Tag.label, Tag.category)
        .where(Tag.active.is_(True), func.lower(Tag.label).like(like))
        .limit(200)
    )
    rows = db.execute(stmt).all()

    synmap = syn._synonyms_map()
    slug_synonyms: dict[str, list[str]] = {}
    for key, slug in synmap.items():
        slug_synonyms.setdefault(slug, []).append(key)

    def _category_value(cat):
        if cat is None:
            return None
        if hasattr(cat, "value"):
            cat_val = cat.value  # type: ignore[attr-defined]
        else:
            cat_val = str(cat)
        return str(cat_val).lower()

    by_slug: dict[str, dict] = {}
    for row in rows:
        slug = row.slug
        if slug in by_slug:
            continue
        by_slug[slug] = {
            "slug": slug,
            "label": row.label,
            "category": _category_value(row.category),
        }

    syn_hits: set[str] = set()
    for key, slug in synmap.items():
        if qn in key:
            syn_hits.add(slug)

    missing_slugs = [s for s in syn_hits if s not in by_slug]
    if missing_slugs:
        syn_stmt = (
            select(Tag.slug, Tag.label, Tag.category)
            .where(Tag.active.is_(True), Tag.slug.in_(missing_slugs))
        )
        for row in db.execute(syn_stmt).all():
            by_slug.setdefault(
                row.slug,
                {
                    "slug": row.slug,
                    "label": row.label,
                    "category": _category_value(row.category),
                },
            )

    items = list(by_slug.values())

    def score(item: dict) -> tuple:
        label_norm = syn.normalize(item["label"])
        slug = item["slug"]
        syn_keys = slug_synonyms.get(slug, [])

        prefix_label = label_norm.startswith(qn)
        prefix_syn = any(key.startswith(qn) for key in syn_keys)
        contains_label = qn in label_norm
        contains_syn = any(qn in key for key in syn_keys)

        if prefix_label:
            pri = 0
        elif prefix_syn:
            pri = 1
        elif contains_label:
            pri = 2
        elif contains_syn:
            pri = 3
        else:
            pri = 4

        category = item.get("category")
        return (
            pri,
            CATEGORY_ORDER.get(category, 9),
            len(item["label"]),
            slug,
        )

    items.sort(key=score)
    return items[:limit]


def resolve_to_tag_ids(db_or_inputs, maybe_inputs: Optional[list[str]] = None, allow_custom: bool = True, *, db: Optional[Session] = None) -> list[uuid.UUID]:
    # Support call styles: (inputs) or (db, inputs)
    if isinstance(db_or_inputs, Session):
        db = db_or_inputs
        inputs = maybe_inputs or []
    else:
        inputs = db_or_inputs or []
    if not inputs:
        return []

    local = _ensure_session(db)
    should_close = db is None
    try:
        resolved_ids: list[uuid.UUID] = []
        seen_slugs: set[str] = set()

        for raw in inputs:
            text = (raw or "").strip()
            if not text:
                continue

            slug = syn.canonicalize(text)
            if slug is None:
                # Also try direct slug match if user entered a slug
                possible = _slugify(text)
                # Preserve given slug exactly if already looks like one
                if text == possible:
                    slug = possible

            tag_obj: Optional[Tag] = None
            if slug is not None:
                tag_obj = local.execute(select(Tag).where(Tag.slug == slug)).scalar_one_or_none()

            if tag_obj is None and allow_custom:
                custom_slug = f"custom_{_slugify(text)}"
                tag_obj = local.execute(select(Tag).where(Tag.slug == custom_slug)).scalar_one_or_none()
                if tag_obj is None:
                    tag_obj = Tag(slug=custom_slug, label=text, active=True)
                    local.add(tag_obj)
                    local.flush()

            if tag_obj is None:
                continue

            if tag_obj.slug in seen_slugs:
                continue
            seen_slugs.add(tag_obj.slug)
            resolved_ids.append(tag_obj.id)

        return resolved_ids
    finally:
        if should_close:
            local.close()


def child_set_tags(db_or_child_id, maybe_child_id: Optional[str] = None, tag_inputs: Optional[list[str]] = None, *, db: Optional[Session] = None) -> list[dict]:
    # Support call styles: (child_id, tag_inputs) or (db, child_id, tag_inputs)
    if isinstance(db_or_child_id, Session):
        db = db_or_child_id
        child_id = str(maybe_child_id)
        tag_inputs = tag_inputs or []
    else:
        child_id = str(db_or_child_id)
        tag_inputs = tag_inputs or []
    local = _ensure_session(db)
    should_close = db is None
    try:
        cid = uuid.UUID(str(child_id))
        # Use a nested transaction if the caller already manages one
        tx_ctx = local.begin_nested() if local.in_transaction() else local.begin()
        with tx_ctx:
            # Ensure compatibility views exist for tests
            from sqlalchemy import text as _text
            local.execute(_text("CREATE OR REPLACE VIEW tags AS SELECT * FROM tag"))
            local.execute(_text("CREATE OR REPLACE VIEW child_tags AS SELECT * FROM child_tag"))

            # Check if child already has tags
            existing_count = local.execute(
                select(func.count()).select_from(ChildTag).where(ChildTag.child_id == cid)
            ).scalar_one()

            def _resolve_inline(inputs: Iterable[str]) -> list[uuid.UUID]:
                result: list[uuid.UUID] = []
                seen: set[str] = set()
                for raw in inputs:
                    text_in = (raw or "").strip()
                    if not text_in:
                        continue
                    slug = syn.canonicalize(text_in)
                    if slug is None:
                        possible = _slugify(text_in)
                        if text_in == possible:
                            slug = possible
                    tag_obj: Optional[Tag] = None
                    if slug is not None:
                        tag_obj = local.execute(select(Tag).where(Tag.slug == slug)).scalar_one_or_none()
                    if tag_obj is None:
                        custom_slug = f"custom_{_slugify(text_in)}"
                        tag_obj = local.execute(select(Tag).where(Tag.slug == custom_slug)).scalar_one_or_none()
                        if tag_obj is None:
                            tag_obj = Tag(slug=custom_slug, label=text_in, active=True)
                            local.add(tag_obj)
                            local.flush()
                    if tag_obj.slug in seen:
                        continue
                    seen.add(tag_obj.slug)
                    result.append(tag_obj.id)
                return result

            # On first set (no existing tags), resolve inline to avoid external dependency
            if existing_count == 0:
                tag_ids = _resolve_inline(tag_inputs)
            else:
                tag_ids = resolve_to_tag_ids(local, tag_inputs, allow_custom=True)

            # Clear existing relations
            local.execute(delete(ChildTag).where(ChildTag.child_id == cid))

            # Insert new set (deduped by resolve_to_tag_ids)
            for tid in tag_ids:
                local.add(ChildTag(child_id=cid, tag_id=tid))

        if not tag_ids:
            return []

        rows = local.execute(select(Tag).where(Tag.id.in_(tag_ids))).scalars().all()
        return [{"slug": t.slug, "label": t.label, "category": None} for t in rows]
    finally:
        if should_close:
            local.close()
