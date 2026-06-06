from datetime import date

from app.core.enums import CalendarTypeEnum
from app.services.date_normalization_service import DateNormalizationService


def test_solar_birth_date_remains_unchanged():
    service = DateNormalizationService()

    normalized, lunar_original = service.normalize_birth_date(
        birth_date=date(2005, 8, 25),
        calendar_type=CalendarTypeEnum.SOLAR,
        is_leap_month=False,
    )

    assert normalized == date(2005, 8, 25)
    assert lunar_original is None


def test_lunar_birth_date_converts_to_solar():
    service = DateNormalizationService()

    normalized, lunar_original = service.normalize_birth_date(
        birth_date=date(2007, 1, 27),
        calendar_type=CalendarTypeEnum.LUNAR,
        is_leap_month=False,
    )

    assert normalized is not None
    assert lunar_original == date(2007, 1, 27)
    assert normalized != lunar_original
