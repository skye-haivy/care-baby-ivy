import re
import pytest
from sqlalchemy import select

# Adjust imports to your actual paths
from app.models.tag import Tag
from app.models.child import ChildProfile
from app.models.tag import Tag
from app.services import tagging
from app.services.synonyms import canonicalize

def _get_child_tag_slugs(db, child_id):
    # Replace with ORM join if you have ChildTag model imported
    from sqlalchemy import text
    rows = db.execute(text("""
        SELECT t.slug FROM child_tags ct
        JOIN tags t ON t.id = ct.tag_id
        WHERE ct.child_id = :cid
        ORDER BY t.slug
    """), {"cid": child_id}).all()
    return [r[0] for r in rows]

@pytest.mark.usefixtures("ensure_seeded")
def test_resolve_known_and_custom_tags(db):
    ids = tagging.resolve_to_tag_ids(db, ["sleep training", "eczema", "unicorn allergy"])
    # Look up slugs for those IDs
    slugs = {db.execute(select(Tag.slug).where(Tag.id == _id)).scalar_one() for _id in ids}
    # Known ones must be canonical
    assert "topic_sleep" in slugs
    assert "cond_eczema" in slugs
    # Unknown becomes custom_*
    custom = [s for s in slugs if s.startswith("custom_")]
    assert len(custom) == 1, "exactly one custom_* should be created"
    assert re.match(r"^custom_[a-z0-9]+$", custom[0])

@pytest.mark.usefixtures("ensure_seeded")
def test_custom_tag_idempotency(db):
    # First resolve creates custom_*
    ids1 = tagging.resolve_to_tag_ids(db, ["unicorn allergy"])
    tag1 = db.execute(select(Tag).where(Tag.id == ids1[0])).scalar_one()
    assert tag1.slug.startswith("custom_")
    # Second resolve should reuse same tag (no new row)
    ids2 = tagging.resolve_to_tag_ids(db, ["unicorn allergy"])
    tag2 = db.execute(select(Tag).where(Tag.id == ids2[0])).scalar_one()
    assert tag2.id == tag1.id

@pytest.mark.usefixtures("ensure_seeded")
def test_deduplicate_inputs(db):
    ids = tagging.resolve_to_tag_ids(db, ["sleep", "Sleep Training", "sleep   training"])
    assert len(ids) == 1, "duplicates should dedupe to one canonical tag id"
    slug = db.execute(select(Tag.slug).where(Tag.id == ids[0])).scalar_one()
    assert slug == "topic_sleep"

@pytest.mark.usefixtures("ensure_seeded")
def test_child_set_tags_replaces_atomically(db, child):
    # First set
    out1 = tagging.child_set_tags(db, child.id, ["sleep", "eczema"])
    slugs1 = sorted([o["slug"] for o in out1])
    assert slugs1 == ["cond_eczema", "topic_sleep"]
    assert _get_child_tag_slugs(db, child.id) == slugs1

    # Replace with different set (including a custom)
    out2 = tagging.child_set_tags(db, child.id, ["peanut intro", "unicorn allergy"])
    slugs2 = sorted([o["slug"] for o in out2])
    assert slugs2[0].startswith("allergy_peanut")
    assert any(s.startswith("custom_") for s in slugs2)
    # Old tags should be gone
    assert _get_child_tag_slugs(db, child.id) == slugs2

@pytest.mark.usefixtures("ensure_seeded")
def test_suggest_from_text_ranking(db):
    # We expect prefix match to come first
    suggestions = tagging.suggest_from_text(db, "ecz")
    labels = [s["label"].lower() for s in suggestions]
    # should include eczema; first item should be eczema-ish
    assert any("eczema" in l for l in labels)
    assert "eczema" in labels[0]

@pytest.mark.usefixtures("ensure_seeded")
def test_transaction_rollback_on_failure(db, child, monkeypatch):
    # Monkeypatch insert to raise after clearing existing tags to ensure rollback
    original = tagging.resolve_to_tag_ids

    def boom(*args, **kwargs):
        raise RuntimeError("kaboom")

    monkeypatch.setattr(tagging, "resolve_to_tag_ids", boom)
    # Pre-insert one tag so we can see if it gets wiped incorrectly
    tagging.child_set_tags(db, child.id, ["sleep"])

    with pytest.raises(RuntimeError):
        tagging.child_set_tags(db, child.id, ["eczema"])  # should rollback entirely

    # Original tag set should still be intact (no partial changes)
    assert _get_child_tag_slugs(db, child.id) == ["topic_sleep"]

    # restore (not strictly needed due to function scope)
    monkeypatch.setattr(tagging, "resolve_to_tag_ids", original)
