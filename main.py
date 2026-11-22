from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Path as PathParameter, Query, Response
from sqlalchemy import URL, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from db import get_session
from models import Review
from schemas import ReviewCreate, ReviewResponse

ReviewId = Annotated[int, PathParameter(gt=0)]


def create_app(database_path: Path | None = None) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        url = URL.create("sqlite+aiosqlite", database=str(app.state.database_path))
        engine = create_async_engine(url)
        app.state.session_factory = async_sessionmaker(engine, expire_on_commit=False)
        try:
            # Схему готовим заранее командой python -m alembic upgrade head.
            yield
        finally:
            await engine.dispose()

    app = FastAPI(
        title="Гостевая книга",
        description="",
        lifespan=lifespan,
    )
    app.state.database_path = (
        database_path if database_path is not None else Path(__file__).with_name("reviews.sqlite3")
    )

    @app.get("/reviews", response_model=list[ReviewResponse], tags=["Отзывы"])
    async def review_list(
        session: AsyncSession = Depends(get_session),
        author: str | None = Query(None, description="Фильтрация по имени автора"),
    ):
        statement = select(Review).order_by(Review.id.desc())
        if author is not None:
            author_clean = author.strip()
            statement = statement.where(Review.author == author_clean)
        result = await session.execute(statement)
        return result.scalars().all()

    @app.get("/reviews/{review_id}", response_model=ReviewResponse, tags=["Отзывы"])
    async def review_get(
        review_id: ReviewId,
        session: AsyncSession = Depends(get_session),
    ):
        review = await session.get(Review, review_id)
        if review is None:
            raise HTTPException(status_code=404, detail="Отзыв не найден")
        return review

    @app.post("/reviews", response_model=ReviewResponse, status_code=201, tags=["Отзывы"])
    async def review_create(
        review: ReviewCreate,
        session: AsyncSession = Depends(get_session),
    ):
        new_review = Review(author=review.author, text=review.text)
        session.add(new_review)
        await session.commit()
        await session.refresh(new_review)
        return new_review

    @app.delete("/reviews/{review_id}", status_code=204, tags=["Отзывы"])
    async def review_delete(
        review_id: ReviewId,
        session: AsyncSession = Depends(get_session),
    ):
        review = await session.get(Review, review_id)
        if review is None:
            raise HTTPException(status_code=404, detail="Отзыв не найден")
        await session.delete(review)
        await session.commit()
        return Response(status_code=204)

    return app


app = create_app()
