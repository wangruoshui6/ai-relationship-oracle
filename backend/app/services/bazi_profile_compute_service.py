from typing import Any


class BaziProfileComputeService:
    def build_user_profile_fields(
        self,
        *,
        birth_date_present: bool,
        birth_time_present: bool,
    ) -> dict[str, Any]:
        if not birth_date_present:
            return {
                "bazi_chart": None,
                "five_elements": None,
            }

        return {
            "bazi_chart": {
                "status": "stub",
                "has_birth_time": birth_time_present,
            },
            "five_elements": {
                "status": "stub",
            },
        }

    def build_partner_profile_fields(
        self,
        *,
        birth_date_present: bool,
        birth_time_present: bool,
    ) -> dict[str, Any]:
        if not birth_date_present:
            return {"bazi_chart": None}

        return {
            "bazi_chart": {
                "status": "stub",
                "has_birth_time": birth_time_present,
            }
        }
