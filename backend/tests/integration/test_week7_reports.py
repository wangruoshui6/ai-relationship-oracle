"""Week 7 tests: ReportService."""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.api.deps import get_db
from app.db.base import Base
from app.main import app

engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


@pytest.fixture
def client() -> TestClient:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    def override_get_db():
        db = TestingSessionLocal()
        try: yield db
        finally: db.close()
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as tc:
        yield tc
    app.dependency_overrides.clear()


def _auth(client, email="rpt@test.com"):
    client.post("/api/v1/auth/register", json={"email": email, "password": "password123"})
    r = client.post("/api/v1/auth/login", json={"email": email, "password": "password123"})
    return {"Authorization": f"Bearer {r.json()['data']['access_token']}"}


class TestReports:
    def test_generate_report_returns_200(self, client):
        h = _auth(client)
        client.put("/api/v1/profiles/me", headers=h, json={"gender": "male", "birth_date": "1998-05-01"})
        r = client.post("/api/v1/partners", headers=h, json={"nickname": "Sarah", "birth_date": "1999-03-10"})
        pid = r.json()["data"]["id"]
        client.post("/api/v1/consultations", headers=h, json={"message": "I broke up with Sarah", "partner_id": pid})

        r = client.post("/api/v1/reports", headers=h, json={"partner_id": pid})
        assert r.status_code == 200
        data = r.json()["data"]
        assert data["id"]
        assert data["title"]
        assert "Sarah" in data["title"]

    def test_list_reports(self, client):
        h = _auth(client, "rpt2@test.com")
        client.put("/api/v1/profiles/me", headers=h, json={"birth_date": "1998-05-01"})
        r = client.post("/api/v1/partners", headers=h, json={"nickname": "Amy"})
        pid = r.json()["data"]["id"]
        client.post("/api/v1/reports", headers=h, json={"partner_id": pid})
        client.post("/api/v1/reports", headers=h, json={"partner_id": pid})

        r = client.get("/api/v1/reports", headers=h)
        assert r.status_code == 200
        assert len(r.json()["data"]) == 2

    def test_get_report_detail(self, client):
        h = _auth(client, "rpt3@test.com")
        client.put("/api/v1/profiles/me", headers=h, json={"birth_date": "1998-05-01"})
        r = client.post("/api/v1/partners", headers=h, json={"nickname": "Lily"})
        pid = r.json()["data"]["id"]
        r = client.post("/api/v1/reports", headers=h, json={"partner_id": pid})
        rid = r.json()["data"]["id"]

        r = client.get(f"/api/v1/reports/{rid}", headers=h)
        assert r.status_code == 200
        assert r.json()["data"]["content_markdown"]

    def test_report_access_isolated_by_user(self, client):
        h1 = _auth(client, "owner@test.com")
        client.put("/api/v1/profiles/me", headers=h1, json={"birth_date": "1998-05-01"})
        r = client.post("/api/v1/partners", headers=h1, json={"nickname": "Target"})
        pid = r.json()["data"]["id"]
        r = client.post("/api/v1/reports", headers=h1, json={"partner_id": pid})
        rid = r.json()["data"]["id"]

        h2 = _auth(client, "other@test.com")
        r = client.get(f"/api/v1/reports/{rid}", headers=h2)
        assert r.status_code == 404

    def test_generate_report_rejects_foreign_partner_id(self, client):
        h1 = _auth(client, "owner2@test.com")
        client.put("/api/v1/profiles/me", headers=h1, json={"birth_date": "1998-05-01"})
        r = client.post("/api/v1/partners", headers=h1, json={"nickname": "ForeignTarget"})
        foreign_partner_id = r.json()["data"]["id"]

        h2 = _auth(client, "other2@test.com")
        r = client.post("/api/v1/reports", headers=h2, json={"partner_id": foreign_partner_id})
        assert r.status_code == 404

    def test_chat_does_not_auto_create_report(self, client):
        h = _auth(client, "rpt5@test.com")
        r = client.post("/api/v1/consultations", headers=h, json={"message": "just chatting"})
        assert r.json()["data"]["report_generated"] is False
