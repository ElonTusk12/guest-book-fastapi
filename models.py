"""ORM-модель SQLAlchemy описывает таблицу отзывов и объекты, связанные с ней."""

from sqlalchemy import CheckConstraint, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Review(Base):
    __tablename__ = "review"
    __table_args__ = (
        CheckConstraint("length(author) BETWEEN 1 AND 100", name="review_author_length"),
        CheckConstraint("length(text) BETWEEN 1 AND 1000", name="review_text_length"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    author: Mapped[str] = mapped_column(String(100), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
