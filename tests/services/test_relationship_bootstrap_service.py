"""Week 4 tests: RelationshipBootstrapService."""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.models.partner_profile import PartnerProfile
from app.services.relationship_bootstrap_service import RelationshipBootstrapService
from app.utils.ids import generate_uuid


@pytest.fixture
def db() -> Session:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine, autoflush=False, autocommit=False)()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def partner(db):
    p = PartnerProfile(
        id=generate_uuid(),
        user_id="user-1",
        nickname="Test Partner",
        relationship_type="unknown",
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


class TestRelationshipBootstrap:
    def test_first_call_creates_both_profile_and_summary(self, db, partner):
        svc = RelationshipBootstrapService(db)
        profile, summary, created = svc.ensure_bootstrap(
            user_id="user-1",
            partner_id=partner.id,
            current_status="breakup",
            current_goal="reconciliation",
            partner_name=partner.nickname,
        )
        assert created is True
        assert profile.user_id == "user-1"
        assert profile.partner_id == partner.id
        assert profile.current_status == "breakup"
        assert profile.updated_by.value == "system"
        assert summary.summary_version == 1
        assert profile.id is not None
        assert summary.id is not None

    def test_second_call_returns_existing(self, db, partner):
        svc = RelationshipBootstrapService(db)
        svc.ensure_bootstrap(
            user_id="user-1",
            partner_id=partner.id,
            current_status="breakup",
            current_goal="reconciliation",
            partner_name=partner.nickname,
        )
        profile2, summary2, created2 = svc.ensure_bootstrap(
            user_id="user-1",
            partner_id=partner.id,
            current_status="conflict",
            current_goal="long_term",
            partner_name=partner.nickname,
        )
        assert created2 is False
        # should still reflect original values since not updated
        assert profile2.current_status == "breakup"

    def test_memory_summary_contains_partner_name(self, db, partner):
        svc = RelationshipBootstrapService(db)
        _, summary, _ = svc.ensure_bootstrap(
            user_id="user-1",
            partner_id=partner.id,
            current_status="breakup",
            current_goal="reconciliation",
            partner_name="Xiao Wang",
        )
        assert "Xiao Wang" in summary.summary

    def test_handles_none_status_and_goal(self, db, partner):
        svc = RelationshipBootstrapService(db)
        profile, summary, created = svc.ensure_bootstrap(
            user_id="user-1",
            partner_id=partner.id,
            current_status=None,
            current_goal=None,
            partner_name=partner.nickname,
        )
        assert created is True
        assert "unknown" in profile.summary_snapshot

    def test_different_user_partner_combos_are_independent(self, db, partner):
        svc = RelationshipBootstrapService(db)
        p1, s1, c1 = svc.ensure_bootstrap(
            user_id="user-1", partner_id=partner.id,
            current_status="breakup", current_goal=None,
            partner_name=partner.nickname,
        )
        # different user
        p2, s2, c2 = svc.ensure_bootstrap(
            user_id="user-2", partner_id=partner.id,
            current_status="current", current_goal=None,
            partner_name=partner.nickname,
        )
        assert c1 is True
        assert c2 is True
        assert p1.id != p2.id
