"""add lower(label) index for tag suggestions

Revision ID: 7e9d1f8c4d13
Revises: 27a92014095d
Create Date: 2024-08-09 00:00:00
"""
from __future__ import annotations

from alembic import op

# revision identifiers, used by Alembic.
revision = "7e9d1f8c4d13"
down_revision = "27a92014095d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE INDEX IF NOT EXISTS idx_tag_label_lower ON tag ((lower(label)));")


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_tag_label_lower;")
