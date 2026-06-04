"""Event Detector Service — Week 5."""
from app.models.relationship_event import RelationshipEvent
from app.models.relationship_event_candidate import RelationshipEventCandidate
from app.utils.ids import generate_uuid


HIGH_CONFIDENCE_PATTERNS = [
    (["broke up", "break up", "split up", "分手", "分开", "离婚", "结束"], "breakup", 0.95),
    (["married", "结婚", "求婚", "engaged", "订婚"], "marriage", 0.95),
    (["moved in", "同居", "move in together"], "cohabitation", 0.85),
    (["pregnant", "怀孕", "有孩子"], "pregnancy", 0.90),
]

LOW_CONFIDENCE_PATTERNS = [
    (["argu", "fought", "fight", "吵架", "争吵", "冷战"], "conflict", 0.60),
    (["blocked", "拉黑", "删了", "不回消息"], "blocking", 0.55),
    (["met parent", "见了父母", "见家长", "见爸妈"], "meeting_parents", 0.50),
    (["travel", "旅行", "旅游", "一起出去玩"], "travel", 0.45),
    (["gift", "礼物", "送了"], "gift_exchange", 0.45),
    (["promotion", "升职", "换工作", "辞职"], "career_change", 0.40),
]


class EventDetectorService:
    def detect(self, user_id: str, partner_id: str, message: str,
               conversation_id: str | None = None,
               ) -> tuple[list[RelationshipEvent], list[RelationshipEventCandidate]]:
        events: list[RelationshipEvent] = []
        candidates: list[RelationshipEventCandidate] = []
        msg = message.lower()

        for patterns, event_type, confidence in HIGH_CONFIDENCE_PATTERNS:
            if self._matches(msg, patterns):
                events.append(self._build_event(user_id, partner_id, event_type, confidence, message))
                break

        for patterns, event_type, confidence in LOW_CONFIDENCE_PATTERNS:
            if self._matches(msg, patterns):
                candidates.append(self._build_candidate(user_id, partner_id, event_type, confidence, message))

        return events, candidates

    def detect_for_consultation(self, user_id: str, partner_id: str, message: str) -> list[RelationshipEvent]:
        events, _ = self.detect(user_id, partner_id, message)
        return events

    @staticmethod
    def _matches(msg: str, patterns: list[str]) -> bool:
        return any(p in msg for p in patterns)

    @staticmethod
    def _build_event(user_id: str, partner_id: str, event_type: str, conf: float, msg: str) -> RelationshipEvent:
        return RelationshipEvent(
            id=generate_uuid(), user_id=user_id, partner_id=partner_id,
            event_type=event_type, event_date=None, description=msg[:500],
            source="auto", confidence_score=conf,
        )

    @staticmethod
    def _build_candidate(user_id: str, partner_id: str, event_type: str, conf: float, msg: str) -> RelationshipEventCandidate:
        return RelationshipEventCandidate(
            id=generate_uuid(), user_id=user_id, partner_id=partner_id,
            event_type=event_type, event_date=None, description=msg[:500],
            source="auto", confidence_score=conf, candidate_status="pending",
        )
