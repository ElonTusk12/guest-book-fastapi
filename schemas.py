"""Pydantic описывает HTTP-данные. ORM-модель находится отдельно в models.py."""

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ReviewCreate(BaseModel):
    author: str = Field(min_length=1, max_length=100)
    text: str = Field(min_length=1, max_length=1000)

    @field_validator("author", "text", mode="before")
    @classmethod
    def strip_and_validate_non_empty(cls, v: object) -> object:
        if isinstance(v, str):
            v_stripped = v.strip()
            if not v_stripped:
                raise ValueError("Поле не может быть пустым или состоять только из пробелов")
            return v_stripped
        return v


class ReviewResponse(BaseModel):
    # Позволяет читать поля ответа из атрибутов ORM-объекта Review.
    model_config = ConfigDict(from_attributes=True)

    id: int
    author: str
    text: str
