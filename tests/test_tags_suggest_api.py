import pytest
from httpx import AsyncClient

from app.main import app


@pytest.mark.asyncio
@pytest.mark.usefixtures("ensure_seeded")
async def test_suggest_prefix_hit():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/tags/suggest", params={"q": "ecz", "limit": 8})
    assert response.status_code == 200
    payload = response.json()
    assert payload["query"] == "ecz"
    labels = [item["label"].lower() for item in payload["results"]]
    assert labels and "eczema" in labels[0]
    assert any("eczema" in label for label in labels)


@pytest.mark.asyncio
@pytest.mark.usefixtures("ensure_seeded")
async def test_suggest_contains_and_synonym():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/tags/suggest", params={"q": "derma"})
    assert response.status_code == 200
    labels = [item["label"].lower() for item in response.json()["results"]]
    assert any("eczema" in label for label in labels)


@pytest.mark.asyncio
@pytest.mark.usefixtures("ensure_seeded")
async def test_suggest_vaccines_via_synonym():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/tags/suggest", params={"q": "sho"})
    assert response.status_code == 200
    slugs = [item["slug"] for item in response.json()["results"]]
    assert "topic_vaccines" in slugs


@pytest.mark.asyncio
@pytest.mark.usefixtures("ensure_seeded")
async def test_suggest_limits_and_validation():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        too_short = await ac.get("/api/v1/tags/suggest", params={"q": "x"})
        assert too_short.status_code == 400

        capped = await ac.get("/api/v1/tags/suggest", params={"q": "ecz", "limit": 50})
    assert capped.status_code == 200
    assert len(capped.json()["results"]) <= 20
