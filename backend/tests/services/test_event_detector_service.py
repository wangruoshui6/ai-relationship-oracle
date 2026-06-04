"""Week 5 tests: EventDetectorService."""
import pytest
from app.services.event_detector_service import EventDetectorService


class TestEventDetector:
    def test_high_confidence_breakup_detected(self):
        detector = EventDetectorService()
        events, candidates = detector.detect("u1", "p1", "We broke up last month")
        assert len(events) == 1
        assert events[0].event_type == "breakup"
        assert events[0].confidence_score >= 0.8

    def test_high_confidence_marriage_detected(self):
        detector = EventDetectorService()
        events, _ = detector.detect("u1", "p1", "He proposed and we got engaged!")
        assert len(events) == 1
        assert events[0].event_type == "marriage"

    def test_low_confidence_conflict_becomes_candidate(self):
        detector = EventDetectorService()
        events, candidates = detector.detect("u1", "p1", "We had a fight yesterday")
        assert len(events) == 0
        assert len(candidates) >= 1
        assert any(c.event_type == "conflict" for c in candidates)

    def test_low_confidence_blocking_becomes_candidate(self):
        detector = EventDetectorService()
        _, candidates = detector.detect("u1", "p1", "She blocked me on WeChat")
        assert any(c.event_type == "blocking" for c in candidates)

    def test_no_event_for_neutral_message(self):
        detector = EventDetectorService()
        events, candidates = detector.detect("u1", "p1", "The weather is nice today")
        assert len(events) == 0
        assert len(candidates) == 0

    def test_chinese_breakup_detected(self):
        detector = EventDetectorService()
        events, _ = detector.detect("u1", "p1", "我们分手了三个月")
        assert len(events) == 1
        assert events[0].event_type == "breakup"

    def test_chinese_conflict_candidate(self):
        detector = EventDetectorService()
        _, candidates = detector.detect("u1", "p1", "最近总是吵架")
        assert any(c.event_type == "conflict" for c in candidates)

    def test_detect_for_consultation_returns_only_events(self):
        detector = EventDetectorService()
        events = detector.detect_for_consultation("u1", "p1", "We got married!")
        assert len(events) == 1
        assert isinstance(events[0], type(
            __import__("app.models.relationship_event", fromlist=["RelationshipEvent"]).RelationshipEvent()
        ))
