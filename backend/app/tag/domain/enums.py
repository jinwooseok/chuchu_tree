from enum import Enum


class TagLevel(str, Enum):
    """태그 레벨"""
    NEWBIE = "NEWBIE"
    BEGINNER = "BEGINNER"
    REQUIREMENT = "REQUIREMENT"
    DETAIL = "DETAIL"
    CHALLENGE = "CHALLENGE"


class ExcludedReason(str, Enum):
    """제외 사유"""
    INSIGNIFICANT = "INSIGNIFICANT"
    COMPREHENSIVE = "COMPREHENSIVE"
    MINOR = "MINOR"