from enum import Enum


class Provider(str, Enum):
    KAKAO = "KAKAO"
    NAVER = "NAVER"
    GOOGLE = "GOOGLE"
    GITHUB = "GITHUB"
    NONE = "NONE"

    @classmethod
    def has_value(cls, value: str) -> bool:
        return value in cls._value2member_map_
    
class TagLevel(str, Enum):
    NEWBIE = "NEWBIE"
    BEGINNER = "BEGINNER"
    REQUIREMENT = "REQUIREMENT"
    DETAIL = "DETAIL"
    CHALLENGE = "CHALLENGE"


class ExcludedReason(str, Enum):
    INSIGNIFICANT = "INSIGNIFICANT"
    COMPREHENSIVE = "COMPREHENSIVE"
    MINOR = "MINOR"


class FilterCode(str, Enum):
    EASY = "EASY"
    NORMAL = "NORMAL"
    HARD = "HARD"
    EXTREME = "EXTREME"


class SkillCode(str, Enum):
    IM = "IM"      # Intermediate
    AD = "AD"      # Advanced
    MAS = "MAS"    # Master