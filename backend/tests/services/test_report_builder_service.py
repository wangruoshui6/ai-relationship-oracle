from app.services.report_builder_service import ReportBuilderService


def test_build_context_prompt_handles_none_bazi_chart():
    service = ReportBuilderService()
    prompt = service._build_context_prompt(
        {
            "user_profile": {
                "gender": "male",
                "birth_date": "1998-05-01",
                "bazi_chart": None,
                "five_elements": None,
            },
            "partner": {
                "nickname": "Sarah",
                "birth_date": "1999-03-10",
                "bazi_chart": None,
            },
            "relationship_profile": None,
            "events": [],
            "summary": None,
        }
    )

    assert "Partner: nickname=Sarah" in prompt
    assert "User: gender=male" in prompt
