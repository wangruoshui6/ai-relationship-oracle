from datetime import date

from lunardate import LunarDate

from app.core.enums import CalendarTypeEnum


class DateNormalizationService:
    def normalize_birth_date(
        self,
        *,
        birth_date: date | None,
        calendar_type: CalendarTypeEnum | None,
        is_leap_month: bool = False,
    ) -> tuple[date | None, date | None]:
        if birth_date is None:
            return None, None

        calendar = calendar_type or CalendarTypeEnum.SOLAR
        if calendar == CalendarTypeEnum.SOLAR:
            return birth_date, None

        lunar_original = birth_date
        solar_date = LunarDate(
            birth_date.year,
            birth_date.month,
            birth_date.day,
            isLeapMonth=is_leap_month,
        ).toSolarDate()
        return solar_date, lunar_original
