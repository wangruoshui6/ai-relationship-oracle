"""Week 4 tests: IntentRouterService."""
import pytest
from app.services.intent_router_service import IntentRouterService


class TestIntentRouter:
    def test_relationship_analysis(self):
        router = IntentRouterService()
        assert router.detect_intent("I broke up with Sarah") == "relationship_analysis"
        assert router.detect_intent("She ignored my messages") == "relationship_analysis"

    def test_greeting(self):
        router = IntentRouterService()
        assert router.detect_intent("Hello") == "greeting"
        assert router.detect_intent("Hi") == "greeting"

    def test_general_guidance_cn(self):
        router = IntentRouterService()
        assert router.detect_intent("事业遇到瓶颈") == "general_guidance"
        assert router.detect_intent("法律咨询") == "general_guidance"
        assert router.detect_intent("健康问题") == "general_guidance"
        assert router.detect_intent("财富管理") == "general_guidance"

    def test_defaults_to_relationship(self):
        router = IntentRouterService()
        assert router.detect_intent("random thoughts about love") == "relationship_analysis"

    def test_handles_empty(self):
        router = IntentRouterService()
        assert router.detect_intent("") == "relationship_analysis"

    def test_case_insensitive(self):
        router = IntentRouterService()
        assert router.detect_intent("HELLO") == "greeting"

    def test_greeting_priority_over_guidance(self):
        router = IntentRouterService()
        assert router.detect_intent("Hi 事业怎么办") == "greeting"
