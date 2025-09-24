import pytest
from httpx import AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_put_and_get_tags_workflow(db_event_loop):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Create child (assumes you have POST /children)
        r = await ac.post(
            "/api/v1/children",
            headers={"X-User-Id": "u1"},
            json={
                "name": "Ava",
                "dob": "2024-12-01",
                "gender": "f",
                "region": "US",
                "language_pref": "en",
            },
        )
        assert r.status_code == 200
        child = r.json()
        cid = child["id"]

        # PUT tags
        r = await ac.put(
            f"/api/v1/children/{cid}/tags",
            headers={"X-User-Id": "u1"},
            json={"tags": ["sleep training", "eczema", "unicorn allergy"]},
        )
        assert r.status_code == 200
        data = r.json()
        slugs = sorted([t["slug"] for t in data["tags"]])
        assert "topic_sleep" in slugs and "cond_eczema" in slugs
        assert any(s.startswith("custom_") for s in slugs)

        # GET tags
        r = await ac.get(f"/api/v1/children/{cid}/tags", headers={"X-User-Id": "u1"})
        assert r.status_code == 200
        got = r.json()
        assert got["child_id"] == cid
        got_slugs = sorted([t["slug"] for t in got["tags"]])
        assert got_slugs == slugs


@pytest.mark.asyncio
async def test_clear_tags_and_ownership(db_event_loop):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Create child as u1
        r = await ac.post(
            "/api/v1/children",
            headers={"X-User-Id": "u1"},
            json={
                "name": "Ben",
                "dob": "2025-01-05",
                "gender": "m",
                "region": "US",
                "language_pref": "en",
            },
        )
        cid = r.json()["id"]

        # Wrong owner
        r = await ac.get(f"/api/v1/children/{cid}/tags", headers={"X-User-Id": "u2"})
        assert r.status_code == 403

        # Clear tags
        r = await ac.put(
            f"/api/v1/children/{cid}/tags",
            headers={"X-User-Id": "u1"},
            json={"tags": []},
        )
        assert r.status_code == 200
        assert r.json()["tags"] == []


@pytest.mark.asyncio
async def test_missing_header_is_unauthorized(db_event_loop):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        r = await ac.get("/api/v1/children/doesnotexist/tags")
        assert r.status_code == 401


# Local event loop fixture for httpx AsyncClient
import asyncio


@pytest.fixture(scope="session")
def db_event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

