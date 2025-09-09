import json
import os
from pathlib import Path
import subprocess
import pytest
from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://app:app@localhost:5432/app")
TAXONOMY_PATH = Path(__file__).resolve().parents[1] / "taxonomy" / "tags_taxonomy.json"
SEED_SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "seed_tags.py"

@pytest.mark.order(0)
def test_seed_idempotent():
    # run seed twice
    subprocess.check_call(["python", str(SEED_SCRIPT)])
    subprocess.check_call(["python", str(SEED_SCRIPT)])

    engine = create_engine(DATABASE_URL, future=True)
    with engine.begin() as conn:
        total = conn.execute(text("SELECT COUNT(*) FROM tags")).scalar_one()
        # taxonomy count should match table count
        wanted = len(json.loads(TAXONOMY_PATH.read_text(encoding="utf-8")))
        assert total >= wanted  # allow pre-existing rows, but not less

        # slugs unique
        dupes = conn.execute(
            text("""
              SELECT slug, COUNT(*) c FROM tags GROUP BY slug HAVING COUNT(*) > 1
            """)
        ).all()
        assert dupes == []
