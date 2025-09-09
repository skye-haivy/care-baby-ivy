from __future__ import annotations

import json
import os
import sys
import uuid
from pathlib import Path

from sqlalchemy import create_engine, select, text
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session


def get_database_url() -> str:
    return os.getenv("DATABASE_URL", "postgresql+psycopg2://app:app@localhost:5432/app")


def load_taxonomy(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    taxonomy_path = repo_root / "taxonomy" / "tags_taxonomy.json"
    if not taxonomy_path.exists():
        print(f"Taxonomy file not found: {taxonomy_path}", file=sys.stderr)
        sys.exit(1)

    tags = load_taxonomy(taxonomy_path)

    # Import models after adjusting sys.path for local execution
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))

    from app.models.tag import Tag  # type: ignore

    engine = create_engine(get_database_url())
    with Session(engine) as session:
        # Ensure a convenient pluralized view exists for consumers/tests
        session.execute(text("CREATE OR REPLACE VIEW tags AS SELECT * FROM tag"))

        values = []
        for t in tags:
            slug = t["slug"].strip()
            label = t.get("label", slug)
            values.append(
                {
                    "id": uuid.uuid4(),
                    "slug": slug,
                    "label": label,
                    # Keep category NULL for now to avoid enum mismatch
                    "category": None,
                    "active": True,
                }
            )

        stmt = insert(Tag.__table__).values(values)
        update_cols = {"label": stmt.excluded.label, "active": text("TRUE")}
        stmt = stmt.on_conflict_do_update(index_elements=[Tag.__table__.c.slug], set_=update_cols)
        session.execute(stmt)
        session.commit()

        count = session.execute(select(text("count(*)")).select_from(Tag.__table__)).scalar_one()
        print(f"Tags count: {count}")


if __name__ == "__main__":
    main()
