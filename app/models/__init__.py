from app.models.base import Base

# Import models so Alembic can discover them via Base.metadata
from app.models.child import ChildProfile  # noqa: F401
from app.models.tag import Tag, ChildTag  # noqa: F401
from app.models.article import ResearchArticle  # noqa: F401

