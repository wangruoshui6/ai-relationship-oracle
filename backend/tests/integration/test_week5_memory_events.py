"""Week 5 integration tests: consultation with memory + events."""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.api.deps import get_db
from app.db.base import Base
from app.main import app

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
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
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def _auth(client, email="w5@test.com"):
    client.post("/api/v1/auth/register", json={"email": email, "password": "password123"})
    r = client.post("/api/v1/auth/login", json={"email": email, "password": "password123"})
    return {"Authorization": f'Bearer {r.json()["data"]["access_token"]}'}


class TestWeek5ConsultationWithEvents:
    def test_breakup_message_creates_event(self, client):
        headers = _auth(client)
        r = client.post("/api/v1/consultations", headers=headers, json={
            "message": "I broke up with Sarah last week and I am heartbroken",
            "analysis_methods": ["bazi"],
        })
        assert r.status_code == 200
        data = r.json()["data"]
        assert data["auto_created_partner"] is True
        assert data["partner_id"] is not None
        assert data["events_detected"] >= 1

    def test_fight_message_creates_candidate(self, client):
        headers = _auth(client, "w5b@test.com")
        r = client.post("/api/v1/consultations", headers=headers, json={
            "message": "Sarah and I had a fight yesterday",
            "analysis_methods": ["psychology"],
        })
        assert r.status_code == 200
        data = r.json()["data"]
        assert data["auto_created_partner"] is True
        assert data["candidates_created"] >= 1

    def test_relationship_memory_endpoint(self, client):
        headers = _auth(client, "w5c@test.com")
        # First consultation to bootstrap
        client.post("/api/v1/consultations", headers=headers, json={
            "message": "I broke up with Sarah last week",
        })
        # Get partner
        r = client.get("/api/v1/partners", headers=headers)
        partner_id = r.json()["data"][0]["id"]

        # Get relationship memory
        r = client.get(f"/api/v1/relationship-memory/{partner_id}", headers=headers)
        assert r.status_code == 200
        data = r.json()["data"]
        assert data["profile"] is not None
        assert data["summary"] is not None
        assert "events" in data
        assert "candidate_count" in data

    def test_patch_relationship_profile(self, client):
        headers = _auth(client, "w5d@test.com")
        client.post("/api/v1/consultations", headers=headers, json={
            "message": "Fighting with Sarah every day",
        })
        r = client.get("/api/v1/partners", headers=headers)
        partner_id = r.json()["data"][0]["id"]

        r = client.patch(
            f"/api/v1/relationship-memory/{partner_id}/profile",
            headers=headers,
            json={"current_status": "conflict", "conflict_level": "high"},
        )
        assert r.status_code == 200
        assert r.json()["data"]["current_status"] == "conflict"
        assert r.json()["data"]["conflict_level"] == "high"

    def test_relationship_memory_rejects_foreign_partner(self, client):
        owner_headers = _auth(client, "owner-memory@test.com")
        client.post("/api/v1/consultations", headers=owner_headers, json={
            "message": "I broke up with Sarah last week",
        })
        r = client.get("/api/v1/partners", headers=owner_headers)
        foreign_partner_id = r.json()["data"][0]["id"]

        other_headers = _auth(client, "other-memory@test.com")
        r = client.get(f"/api/v1/relationship-memory/{foreign_partner_id}", headers=other_headers)
        assert r.status_code == 404

    def test_event_candidates_confirm_reject(self, client):
        headers = _auth(client, "w5e@test.com")
        client.post("/api/v1/consultations", headers=headers, json={
            "message": "Blocked by Sarah on WeChat",
        })
        r = client.get("/api/v1/partners", headers=headers)
        partner_id = r.json()["data"][0]["id"]

        # List candidates
        r = client.get(
            f"/api/v1/relationship-event-candidates?partner_id={partner_id}",
            headers=headers,
        )
        assert r.status_code == 200
        candidates = r.json()["data"]
        assert len(candidates) >= 1

        # Reject first
        cid = candidates[0]["id"]
        r = client.post(
            f"/api/v1/relationship-event-candidates/{cid}/reject",
            headers=headers,
        )
        assert r.status_code == 200
        assert r.json()["data"]["status"] == "rejected"
