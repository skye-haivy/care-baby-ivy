"""init child/tag/article tables

Revision ID: 202409080001
Revises: 
Create Date: 2025-09-08 00:01:00.000000

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "202409080001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Enums
    gender = sa.Enum("female", "male", "other", "undisclosed", name="gender")
    tag_category = sa.Enum(
        "general", "development", "nutrition", "medical", "other", name="tag_category"
    )

    gender.create(op.get_bind(), checkfirst=True)
    tag_category.create(op.get_bind(), checkfirst=True)

    # child_profile
    op.create_table(
        "child_profile",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("dob", sa.Date(), nullable=True),
        sa.Column("gender", gender, nullable=True),
        sa.Column("region", sa.String(length=120), nullable=True),
        sa.Column("language_pref", sa.String(length=50), nullable=True),
        sa.Column("age_stage", sa.String(length=50), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    # tag
    op.create_table(
        "tag",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("slug", sa.String(length=100), nullable=False),
        sa.Column("label", sa.String(length=200), nullable=False),
        sa.Column("category", tag_category, nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.UniqueConstraint("slug", name="uq_tag_slug"),
    )

    # child_tag
    op.create_table(
        "child_tag",
        sa.Column("child_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tag_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(["child_id"], ["child_profile.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tag_id"], ["tag.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("child_id", "tag_id", name="pk_child_tag"),
        sa.UniqueConstraint("child_id", "tag_id", name="uq_child_tag_pair"),
    )

    # research_article
    op.create_table(
        "research_article",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("source", sa.String(length=200), nullable=False),
        sa.Column("pub_date", sa.Date(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("research_article")
    op.drop_table("child_tag")
    op.drop_table("tag")
    op.drop_table("child_profile")

    # drop enums
    sa.Enum(name="gender").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="tag_category").drop(op.get_bind(), checkfirst=True)

