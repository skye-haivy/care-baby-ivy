import os
import uuid
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Adjust to your actual metadata import
from app.core.db import Base  # if you expose metadata via Base = declarative_base()
from app.models.child import ChildProfile
from app.models.tag import Tag

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/postgres")

@pytest.fixture(scope="session")
def engine():
    engine = create_engine(DATABASE_URL, future=True)
    yield engine
    engine.dispose()

@pytest.fixture(scope="function")
def db(engine):
    # function-scoped transaction so each test is isolated
    conn = engine.connect()
    tx = conn.begin()
    Session = sessionmaker(bind=conn, autoflush=False, autocommit=False, future=True)
    session = Session()
    try:
        yield session
    finally:
        session.close()
        tx.rollback()
        conn.close()

@pytest.fixture
def child(db):
    c = ChildProfile(
        id=str(uuid.uuid4()),
        user_id="u_test",
        name="Ava",
        dob="2024-12-01",
        gender="f",
        region="US",
        language_pref="en",
        age_stage="age_6_12m",
    )
    db.add(c)
    db.commit()
    db.refresh(c)
    return c

@pytest.fixture
def ensure_seeded(db):
    """Assert that canonical tags from Day 3 seeding exist before running tests."""
    required_slugs = {
        "topic_sleep", "topic_naps", "topic_feeding", "topic_weaning",
        "topic_allergies", "allergy_peanut", "cond_eczema"
    }
    slugs = {t.slug for t in db.query(Tag).all()}
    missing = required_slugs - slugs
    if missing:
        pytest.skip(f"Seed missing canonical tags: {missing}")
