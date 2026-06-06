from fastapi.testclient import TestClient

from app.api.deps import get_db
from app.db.base import Base
from app.main import app
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import pytest


engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


@pytest.fixture
def client() -> TestClient:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as tc:
        yield tc
    app.dependency_overrides.clear()


def test_create_evaluation_run_executes_cases(client):
    response = client.post(
        "/api/v1/evaluation/runs",
        json={"run_name": "smoke-eval", "model_name": "deepseek-chat", "prompt_version": "v1"},
    )

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["id"]
    assert payload["status"] == "completed"
    assert payload["total_cases"] >= 1


def test_get_evaluation_run_returns_results(client):
    create_response = client.post(
        "/api/v1/evaluation/runs",
        json={"run_name": "detail-eval", "model_name": "deepseek-chat", "prompt_version": "v1"},
    )
    run_id = create_response.json()["data"]["id"]

    response = client.get(f"/api/v1/evaluation/runs/{run_id}")

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["run"]["id"] == run_id
    assert isinstance(payload["results"], list)
