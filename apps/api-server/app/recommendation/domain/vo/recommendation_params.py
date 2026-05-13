from dataclasses import dataclass, field


@dataclass
class RecommendationParams:
    """추천 파라미터 VO"""
    count: int
    exclusion_mode: str
    level_filter_codes: list[str] | None = None
    tag_filter_codes: list[str] | None = None
    target_user_account_id: int | None = None
    recommend_all_unsolved: bool = False

    def to_dict(self) -> dict:
        return {
            "count": self.count,
            "exclusion_mode": self.exclusion_mode,
            "level_filter_codes": self.level_filter_codes,
            "tag_filter_codes": self.tag_filter_codes,
            "target_user_account_id": self.target_user_account_id,
            "recommend_all_unsolved": self.recommend_all_unsolved,
        }

    @staticmethod
    def from_dict(data: dict) -> "RecommendationParams":
        return RecommendationParams(
            count=data.get("count", 3),
            exclusion_mode=data.get("exclusion_mode", "LENIENT"),
            level_filter_codes=data.get("level_filter_codes"),
            tag_filter_codes=data.get("tag_filter_codes"),
            target_user_account_id=data.get("target_user_account_id"),
            recommend_all_unsolved=data.get("recommend_all_unsolved", False),
        )
