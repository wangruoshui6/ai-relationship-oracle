"""Bazi (Four Pillars of Destiny) calculation service.

Computes the full Bazi chart from a Gregorian birth date and time:
- Year Pillar (Heavenly Stem + Earthly Branch)
- Month Pillar
- Day Pillar
- Hour Pillar
- Five Elements distribution
- Day Master identification
"""
from datetime import date, time, timedelta
from typing import Any


# Heavenly Stems (天干)
HEAVENLY_STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
# Earthly Branches (地支)
EARTHLY_BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
# Five Elements for each Heavenly Stem
STEM_ELEMENTS = {
    "甲": "木", "乙": "木",
    "丙": "火", "丁": "火",
    "戊": "土", "己": "土",
    "庚": "金", "辛": "金",
    "壬": "水", "癸": "水",
}
# Five Elements for each Earthly Branch (main qi)
BRANCH_ELEMENTS = {
    "子": "水", "丑": "土", "寅": "木", "卯": "木",
    "辰": "土", "巳": "火", "午": "火", "未": "土",
    "申": "金", "酉": "金", "戌": "土", "亥": "水",
}
# Chinese Zodiac animals mapped by branch
ZODIAC_BY_BRANCH = {
    "子": "鼠", "丑": "牛", "寅": "虎", "卯": "兔",
    "辰": "龙", "巳": "蛇", "午": "马", "未": "羊",
    "申": "猴", "酉": "鸡", "戌": "狗", "亥": "猪",
}
# Month branch start dates (approx solar terms, indexed by branch index 2-12,0,1 = 寅卯辰...)
# Each entry: (month_branch_index, approx_day_of_month)
MONTH_STARTS = [
    (2, 4),   # 寅 (Feb 4, Li Chun)
    (3, 6),   # 卯 (Mar 6, Jing Zhe)
    (4, 5),   # 辰 (Apr 5, Qing Ming)
    (5, 6),   # 巳 (May 6, Li Xia)
    (6, 6),   # 午 (Jun 6, Mang Zhong)
    (7, 7),   # 未 (Jul 7, Xiao Shu)
    (8, 8),   # 申 (Aug 8, Li Qiu)
    (9, 8),   # 酉 (Sep 8, Bai Lu)
    (10, 8),  # 戌 (Oct 8, Han Lu)
    (11, 8),  # 亥 (Nov 8, Li Dong)
    (0, 7),   # 子 (Dec 7, Da Xue)
    (1, 6),   # 丑 (Jan 6, Xiao Han)
]


class BaziProfileComputeService:
    """Computes Bazi charts from Gregorian birth dates."""

    def compute(self, *, birth_date: date, birth_time: time | None = None) -> dict[str, Any]:
        year_stem, year_branch = self._year_pillar(birth_date)
        month_stem, month_branch = self._month_pillar(birth_date.year, birth_date.month, birth_date.day)
        day_stem, day_branch = self._day_pillar(birth_date)
        hour_stem, hour_branch = self._hour_pillar(day_stem, birth_time) if birth_time else (None, None)

        pillars = [
            {"pillar": "年", "stem": year_stem, "branch": year_branch,
             "stem_element": STEM_ELEMENTS[year_stem], "branch_element": BRANCH_ELEMENTS[year_branch]},
            {"pillar": "月", "stem": month_stem, "branch": month_branch,
             "stem_element": STEM_ELEMENTS[month_stem], "branch_element": BRANCH_ELEMENTS[month_branch]},
            {"pillar": "日", "stem": day_stem, "branch": day_branch,
             "stem_element": STEM_ELEMENTS[day_stem], "branch_element": BRANCH_ELEMENTS[day_branch]},
        ]
        if hour_stem:
            pillars.append({"pillar": "时", "stem": hour_stem, "branch": hour_branch,
                            "stem_element": STEM_ELEMENTS[hour_stem], "branch_element": BRANCH_ELEMENTS[hour_branch]})

        elements_count = self._count_elements(pillars)

        return {
            "bazi_chart": {
                "pillars": pillars,
                "day_master": day_stem,
                "day_master_element": STEM_ELEMENTS[day_stem],
                "zodiac": ZODIAC_BY_BRANCH[year_branch],
                "has_birth_time": birth_time is not None,
            },
            "five_elements": elements_count,
        }

    # ---- Profile Service API (backward compatible) ----
    def build_user_profile_fields(
        self, *, birth_date_present: bool, birth_time_present: bool,
        birth_date: date | None = None, birth_time: time | None = None,
    ) -> dict[str, Any]:
        if not birth_date_present or birth_date is None:
            return {"bazi_chart": None, "five_elements": None}
        return self.compute(birth_date=birth_date, birth_time=birth_time if birth_time_present else None)

    def build_partner_profile_fields(
        self, *, birth_date_present: bool, birth_time_present: bool,
        birth_date: date | None = None, birth_time: time | None = None,
    ) -> dict[str, Any]:
        if not birth_date_present or birth_date is None:
            return {"bazi_chart": None}
        return self.compute(birth_date=birth_date, birth_time=birth_time if birth_time_present else None)

    # ---- Pillar Calculation ----

    def _year_pillar(self, dt: date) -> tuple[str, str]:
        # The Chinese year starts at Li Chun (~Feb 4). Before that, use previous year.
        year = dt.year
        if dt.month < 2 or (dt.month == 2 and dt.day < 4):
            year -= 1
        # 1984 is Jia-Zi (甲子) year
        offset = (year - 1984) % 60
        stem_idx = offset % 10
        branch_idx = offset % 12
        return HEAVENLY_STEMS[stem_idx], EARTHLY_BRANCHES[branch_idx]

    def _month_pillar(self, year: int, month: int, day: int) -> tuple[str, str]:
        # Determine which branch the month belongs to
        month_branch_idx = None
        for branch_idx, start_day in MONTH_STARTS:
            if month == branch_idx + 1 or (month == (branch_idx + 1) % 12 + 1):
                pass  # approximate

        # Simplified: determine month branch by solar term approximation
        # The month pillar branch rotates: 寅 for month containing Li Chun, etc.
        test_date = date(year, month, day)
        branch_idx = self._month_branch_from_date(test_date)

        # Month stem: based on year stem
        # Rule: 甲己之年丙作首 (Jia/Ji year starts with Bing-寅)
        year_stem, _ = self._year_pillar(test_date)
        year_stem_idx = HEAVENLY_STEMS.index(year_stem)
        # The month stem for 寅 (branch_idx=2) based on year stem
        base_stems = [2, 4, 6, 8, 0, 2, 4, 6, 8, 0]  # 甲->丙(2), 乙->戊(4)...
        base = base_stems[year_stem_idx]
        stem_idx = (base + (branch_idx - 2) % 12) % 10

        return HEAVENLY_STEMS[stem_idx], EARTHLY_BRANCHES[branch_idx]

    def _month_branch_from_date(self, dt: date) -> int:
        # Approximate month branch based on month and day
        m, d = dt.month, dt.day
        if (m == 2 and d >= 4) or (m == 3 and d < 6):
            return 2  # 寅
        if (m == 3 and d >= 6) or (m == 4 and d < 5):
            return 3  # 卯
        if (m == 4 and d >= 5) or (m == 5 and d < 6):
            return 4  # 辰
        if (m == 5 and d >= 6) or (m == 6 and d < 6):
            return 5  # 巳
        if (m == 6 and d >= 6) or (m == 7 and d < 7):
            return 6  # 午
        if (m == 7 and d >= 7) or (m == 8 and d < 8):
            return 7  # 未
        if (m == 8 and d >= 8) or (m == 9 and d < 8):
            return 8  # 申
        if (m == 9 and d >= 8) or (m == 10 and d < 8):
            return 9  # 酉
        if (m == 10 and d >= 8) or (m == 11 and d < 8):
            return 10  # 戌
        if (m == 11 and d >= 8) or (m == 12 and d < 7):
            return 11  # 亥
        if (m == 12 and d >= 7) or (m == 1 and d < 6):
            return 0  # 子
        return 1  # 丑 (Jan 6 - Feb 3)

    def _day_pillar(self, dt: date) -> tuple[str, str]:
        # Known reference: 1900-01-01 is 甲戌 (stem_idx=0, branch_idx=10)
        ref = date(1900, 1, 1)
        delta = (dt - ref).days
        stem_idx = (0 + delta) % 10
        branch_idx = (10 + delta) % 12
        return HEAVENLY_STEMS[stem_idx], EARTHLY_BRANCHES[branch_idx]

    def _hour_pillar(self, day_stem: str, birth_time: time) -> tuple[str, str] | tuple[None, None]:
        # Hour branch: 23-01=子(0), 01-03=丑(1), ...
        hour = birth_time.hour
        branch_idx = ((hour + 1) // 2) % 12

        # Hour stem: based on day stem
        # Rule: 甲己还加甲 (Jia/Ji day -> Jia-子)
        day_stem_idx = HEAVENLY_STEMS.index(day_stem)
        base_stems = [0, 2, 4, 6, 8, 0, 2, 4, 6, 8]  # 甲->甲(0), 乙->丙(2)...
        base = base_stems[day_stem_idx]
        stem_idx = (base + branch_idx) % 10

        return HEAVENLY_STEMS[stem_idx], EARTHLY_BRANCHES[branch_idx]

    def _count_elements(self, pillars: list[dict]) -> dict[str, Any]:
        counts = {"木": 0, "火": 0, "土": 0, "金": 0, "水": 0}
        details = []
        for p in pillars:
            counts[p["stem_element"]] += 1
            counts[p["branch_element"]] += 1
            details.append(f"{p['pillar']}柱: {p['stem']}{p['branch']} ({p['stem_element']}+{p['branch_element']})")
        return {"counts": counts, "details": details, "dominant": max(counts, key=counts.get)}
