from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "review",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("author", sa.String(length=100), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.CheckConstraint("length(author) BETWEEN 1 AND 100", name="review_author_length"),
        sa.CheckConstraint("length(text) BETWEEN 1 AND 1000", name="review_text_length"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("review")
