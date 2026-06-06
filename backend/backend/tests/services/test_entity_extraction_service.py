"""Week 4 tests: EntityExtractionService."""
import pytest
from app.services.entity_extraction_service import EntityExtractionService


class TestEntityExtraction:
    def test_extracts_english_partner_name(self):
        extractor = EntityExtractionService()
        result = extractor.extract("I broke up with Sarah last week")
        assert result["partner_name"] == "Sarah"

    def test_extracts_chinese_partner_name_with_he(self):
        extractor = EntityExtractionService()
        result = extractor.extract("我和李静分手了，还有可能复合吗")
        assert result["partner_name"] == "李静"

    def test_extracts_chinese_partner_name_with_recent(self):
        extractor = EntityExtractionService()
        result = extractor.extract("跟张三最近总吵架")
        assert result["partner_name"] == "张三"

    def test_infers_status_breakup(self):
        extractor = EntityExtractionService()
        result = extractor.extract("分手后我很痛苦")
        assert result["current_status"] == "breakup"

    def test_infers_status_ambiguous(self):
        extractor = EntityExtractionService()
        result = extractor.extract("我们关系有点暧昧")
        assert result["current_status"] == "ambiguous"

    def test_infers_status_conflict(self):
        extractor = EntityExtractionService()
        result = extractor.extract("我们天天吵架")
        assert result["current_status"] == "conflict"

    def test_infers_goal_reconciliation(self):
        extractor = EntityExtractionService()
        result = extractor.extract("我想挽回她")
        assert result["current_goal"] == "reconciliation"

    def test_infers_goal_long_term(self):
        extractor = EntityExtractionService()
        result = extractor.extract("我们应该结婚吗")
        assert result["current_goal"] == "long_term_commitment"

    def test_no_extraction_for_empty_message(self):
        extractor = EntityExtractionService()
        result = extractor.extract("hello world")
        assert result["partner_name"] is None
        assert result["current_status"] is None
        assert result["current_goal"] is None

    def test_returns_dict_with_all_keys(self):
        extractor = EntityExtractionService()
        result = extractor.extract("some message")
        assert "partner_name" in result
        assert "current_status" in result
        assert "current_goal" in result
