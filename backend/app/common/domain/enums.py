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
    STUDY_INVITATION = "STUDY_INVITATION"
    STUDY_APPLICATION = "STUDY_APPLICATION"
    STUDY_PROBLEM = "STUDY_PROBLEM"
    USER_PROBLEM = "USER_PROBLEM"
    USER_TIER = "USER_TIER"
    SYSTEM_ANNOUNCEMENT = "SYSTEM_ANNOUNCEMENT"


class NoticeCategoryDetail(str, Enum):
    REQUESTED_STUDY_INVITATION = "REQUESTED_STUDY_INVITATION"
    RESPONSED_STUDY_INVITATION = "RESPONSED_STUDY_INVITATION"
    REQUESTED_STUDY_APPLICATION = "REQUESTED_STUDY_APPLICATION"
    RESPONSED_STUDY_APPLICATION = "RESPONSED_STUDY_APPLICATION"
    ASSIGNED_STUDY_PROBLEM = "ASSIGNED_STUDY_PROBLEM"
    UPDATED_USER_PROBLEM = "UPDATED_USER_PROBLEM"
    UPDATED_USER_TIER = "UPDATED_USER_TIER"
    SYSTEM_ANNOUNCEMENT = "SYSTEM_ANNOUNCEMENT"