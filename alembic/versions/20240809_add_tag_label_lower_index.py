"""add lower(label) index for tag suggestions

Revision ID: 20240809_add_tag_label_lower_index
Revises: None
Create Date: 2024-08-09
"""

from alembic import op


revision = "20240809_add_tag_label_lower_index"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE INDEX IF NOT EXISTS idx_tag_label_lower ON tag ((lower(label)));")


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_tag_label_lower;")
