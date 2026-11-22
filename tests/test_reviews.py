import pytest
from fastapi.testclient import TestClient

from main import create_app


@pytest.fixture
def client(database_path):
    # Таблица уже создана Alembic в изолированной тестовой базе.
    with TestClient(create_app(database_path)) as test_client:
        yield test_client


def test_create_and_read_reviews(client):
    assert client.get("/reviews").json() == []
    response = client.post("/reviews", json={"author": "Иван", "text": "Прекрасный сервис!"})
    assert response.status_code == 201
    review = response.json()
    assert review == {"id": 1, "author": "Иван", "text": "Прекрасный сервис!"}
    assert client.get("/reviews").json() == [review]


def test_invalid_input_is_rejected(client, payload, loc):
    response = client.post("/reviews", json=payload)
    assert response.status_code == 422
    locs = [err["loc"][-1] for err in response.json()["detail"]]
    assert loc in locs
    assert client.get("/reviews").json() == []


def test_get_review_by_id(client):
    created = client.post("/reviews", json={"author": "Олег", "text": "Всё супер"}).json()
    response = client.get(f"/reviews/{created['id']}")
    assert response.status_code == 200
    assert response.json() == created


def test_get_nonexistent_review_returns_404(client):
    response = client.get("/reviews/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Отзыв не найден"}


@pytest.mark.parametrize("review_id", ["abc", "0", "-1"])
def test_path_parameter_is_validated(client, review_id):
    assert client.get(f"/reviews/{review_id}").status_code == 422
    assert client.delete(f"/reviews/{review_id}").status_code == 422


def test_filter_reviews_by_author(client):
    r1 = client.post("/reviews", json={"author": "Иван", "text": "Отзыв 1"}).json()
    r2 = client.post("/reviews", json={"author": "Мария", "text": "Отзыв 2"}).json()
    r3 = client.post("/reviews", json={"author": "Иван", "text": "Отзыв 3"}).json()

    all_reviews = client.get("/reviews").json()
    assert all_reviews == [r3, r2, r1]

    ivan_reviews = client.get("/reviews?author=Иван").json()
    assert ivan_reviews == [r3, r1]

    maria_reviews = client.get("/reviews?author=Мария").json()
    assert maria_reviews == [r2]

    ivan_stripped_filter = client.get("/reviews?author=%20%20Иван%20%20").json()
    assert ivan_stripped_filter == [r3, r1]

    unknown_reviews = client.get("/reviews?author=Неизвестный").json()
    assert unknown_reviews == []


def test_delete_nonexistent_review_returns_404(client):
    response = client.delete("/reviews/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Отзыв не найден"}


def test_openapi_describes_real_api(client):
    schema = client.get("/openapi.json").json()
    assert set(schema["paths"]["/reviews"]) == {"get", "post"}
    assert "201" in schema["paths"]["/reviews"]["post"]["responses"]
    assert set(schema["paths"]["/reviews/{review_id}"]) == {"get", "delete"}
    assert "ReviewCreate" in schema["components"]["schemas"]
    assert "ReviewResponse" in schema["components"]["schemas"]
    assert client.get("/docs").status_code == 200
