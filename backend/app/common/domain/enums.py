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

class ExclusionMode(str, Enum):
    LENIENT = "LENIENT"  # Problems can be recommended via non-excluded tags
    STRICT = "STRICT"    # Problems with ANY excluded tag are filtered out

class SkillCode(str, Enum):
    IM = "IM"      # Intermediate
    AD = "AD"      # Advanced
    MAS = "MAS"    # Master


class SystemLogType(str, Enum):
    SCHEDULER = "SCHEDULER"
    REFRESH = "REFRESH"
    BULK_UPDATE = "BULK_UPDATE"
    PROBLEM_METADATA = "PROBLEM_METADATA"
    WEEKLY_UPDATE = "WEEKLY_UPDATE"


class SystemLogStatus(str, Enum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


class MetadataEntityType(str, Enum):
    PROBLEM = "PROBLEM"
    TAG_PROFICIENCY = "TAG_PROFICIENCY"
    RECOMMENDATION_FILTER = "RECOMMENDATION_FILTER"


class StudyMemberRole(str, Enum):
    OWNER = "OWNER"
    MEMBER = "MEMBER"


class InvitationStatus(str, Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"


class ApplicationStatus(str, Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"


class NoticeCategory(str, Enum):
    STUDY_INVITATION_STATUS = "STUDY_INVITATION_STATUS"
    STUDY_APPLICATION_STATUS = "STUDY_APPLICATION_STATUS"
    STUDY_PROBLEMS_STATUS = "STUDY_PROBLEMS_STATUS"
    USER_PROBLEMS_STATUS = "USER_PROBLEMS_STATUS"
    USER_TIER_STATUS = "USER_TIER_STATUS"
    SYSTEM_ANNOUNCEMENT = "SYSTEM_ANNOUNCEMENT"