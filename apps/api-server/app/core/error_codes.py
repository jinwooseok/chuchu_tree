
# core/exceptions/error_codes.py
from enum import Enum
from typing import NamedTuple


class ErrorCodeInfo(NamedTuple):
    """에러 코드 정보"""
    code: str
    message: str
    status_code: int
    
class ErrorCode(Enum):
    INTERNAL_SERVER_ERROR = ErrorCodeInfo(
        code="INTERNAL_SERVER_ERROR",
        message="오류가 발생했습니다.",
        status_code=500
    )
    
    AUTHORIZATION_FAILED = ErrorCodeInfo(
        code="AUTHORIZATION_FAILED",
        message="인증에 실패했습니다.",
        status_code=401
    )
    
    SOCIAL_LOGIN_FAILED = ErrorCodeInfo(
        code="SOCIAL_LOGIN_FAILED",
        message="소셜 로그인에 실패했습니다.",
        status_code=401
    )
    
    INVALID_PROVIDER = ErrorCodeInfo(
        code="INVALID_PROVIDER",
        message="유효하지 않은 제공자입니다.",
        status_code=400
    )
    
    NO_LOGIN_STATUS = ErrorCodeInfo(
        code="NO_LOGIN_STATUS",
        message="로그인된 상태가 아닙니다.",
        status_code=401
    )
    
    LOGIN_STATUS = ErrorCodeInfo(
        code="LOGIN_STATUS",
        message="이미 로그인된 상태입니다.",
        status_code=401
    )
    
    EXPIRED_TOKEN = ErrorCodeInfo(
        code="EXPIRED_TOKEN",
        message="만료된 토큰입니다.",
        status_code=401
    )
    
    INVALID_TOKEN = ErrorCodeInfo(
        code="INVALID_TOKEN",
        message="유효하지 않은 토큰입니다.",
        status_code=401
    )
    
    INVALID_PASSWORD = ErrorCodeInfo(
        code="INVALID_PASSWORD",
        message="틀린 비밀번호입니다.",
        status_code=401
    )

    INVALID_PASSWORD_FORMAT = ErrorCodeInfo(
        code="INVALID_PASSWORD_FORMAT",
        message="비밀번호 형식이 올바르지 않습니다.",
        status_code=400
    )

    INVALID_EMAIL_FORMAT = ErrorCodeInfo(
        code="INVALID_EMAIL_FORMAT",
        message="이메일 형식이 올바르지 않습니다.",
        status_code=400
    )

    MISSING_REQUIRED_FIELD = ErrorCodeInfo(
        code="MISSING_REQUIRED_FIELD",
        message="필수 입력값이 누락되었습니다.",
        status_code=400
    )

    INVALID_INPUT_TYPE = ErrorCodeInfo(
        code="INVALID_INPUT_TYPE",
        message="입력값의 형식이 올바르지 않습니다.",
        status_code=400
    )

    INPUT_TOO_SHORT = ErrorCodeInfo(
        code="INPUT_TOO_SHORT",
        message="입력값이 너무 짧습니다.",
        status_code=400
    )

    DATABASE_ERROR = ErrorCodeInfo(
        code="DATABASE_ERROR",
        message="데이터베이스 에러가 발생했습니다.",
        status_code=422
    )
    
    PERMISSION_DENIED = ErrorCodeInfo(
        code="PERMISSION_DENIED",
        message="권한이 없습니다.",
        status_code=403
    )
    
    IS_ALREALY_LINKED = ErrorCodeInfo(
        code="IS_ALREALY_LINKED",
        message="이미 연동된 계정입니다.",
        status_code=400
    )
    
    INVALID_ID_VALUE = ErrorCodeInfo(
        code="INVALID_ID_VALUE",
        message="올바르지 않은 아이디입니다.",
        status_code=400
    )
    
    INVALID_INPUT_VALUE = ErrorCodeInfo(
        code="INVALID_INPUT_VALUE",
        message="올바르지 않은 값이 입력됐습니다.",
        status_code=400
    )

    INVALID_REQUEST = ErrorCodeInfo(
        code="INVALID_REQUEST",
        message="잘못된 요청입니다.",
        status_code=400
    )

    INVALID_CSRF_TOKEN = ErrorCodeInfo(
        code="INVALID_CSRF_TOKEN",
        message="CSRF 토큰 검증에 실패했습니다.",
        status_code=403
    )

    EXTERNAL_API_ERROR = ErrorCodeInfo(
        code="EXTERNAL_API_ERROR",
        message="외부 API 호출 중 오류가 발생했습니다.",
        status_code=502
    )

    BAEKJOON_USER_NOT_FOUND = ErrorCodeInfo(
        code="BAEKJOON_USER_NOT_FOUND",
        message="백준 유저를 찾을 수 없습니다.",
        status_code=404
    )
    
    UNLINKED_USER = ErrorCodeInfo(
        code="UNLINKED_USER",
        message="백준 계정과 연동되지 않았습니다.",
        status_code=404
    )
    
    DUPLICATED_ORDER = ErrorCodeInfo(
        code="DUPLICATED_ORDER",
        message="순서가 중복입니다.",
        status_code=400
    )
    
    TAG_NOT_FOUND = ErrorCodeInfo(
        code="TAG_NOT_FOUND",
        message="태그 정보를 찾을 수 없습니다.",
        status_code=400
    )
    
    LINK_COOLDOWN_PERIOD = ErrorCodeInfo(
        code="LINK_COOLDOWN_PERIOD",
        message="마지막 계정 변경 이후 7일이 지나지 않았습니다.",
        status_code=400
    )

    ALREADY_SOLVED_PROBLEM = ErrorCodeInfo(
        code="ALREADY_SOLVED_PROBLEM",
        message="이미 푼 문제입니다.",
        status_code=400
    )

    PROBLEM_ALREADY_RECORDED_ON_DIFFERENT_DATE = ErrorCodeInfo(
        code="PROBLEM_ALREADY_RECORDED_ON_DIFFERENT_DATE",
        message="이미 다른 날짜에 기록된 문제입니다.",
        status_code=400
    )

    TOKEN_REUSE_DETECTED = ErrorCodeInfo(
        code="TOKEN_REUSE_DETECTED",
        message="토큰 재사용이 감지되었습니다. 보안을 위해 모든 세션이 종료됩니다.",
        status_code=401
    )

    CANNOT_MOVE_TO_LATER_DATE = ErrorCodeInfo(
        code="CANNOT_MOVE_TO_LATER_DATE",
        message="이미 기록된 날짜보다 더 최근 날짜로 이동할 수 없습니다.",
        status_code=400
    )

    USER_CODE_EXHAUSTED = ErrorCodeInfo(
        code="USER_CODE_EXHAUSTED",
        message="유저 코드를 생성할 수 없습니다. 잠시 후 다시 시도해 주세요.",
        status_code=500
    )

    BJ_ACCOUNT_NOT_LINKED = ErrorCodeInfo(
        code="BJ_ACCOUNT_NOT_LINKED",
        message="백준 계정이 연동되지 않은 유저입니다.",
        status_code=400
    )

    STUDY_NOT_FOUND = ErrorCodeInfo(
        code="STUDY_NOT_FOUND",
        message="스터디를 찾을 수 없습니다.",
        status_code=404
    )

    STUDY_NAME_ALREADY_TAKEN = ErrorCodeInfo(
        code="STUDY_NAME_ALREADY_TAKEN",
        message="이미 사용 중인 스터디 이름입니다.",
        status_code=400
    )

    STUDY_FULL = ErrorCodeInfo(
        code="STUDY_FULL",
        message="스터디 정원이 가득 찼습니다.",
        status_code=400
    )

    STUDY_ALREADY_MEMBER = ErrorCodeInfo(
        code="STUDY_ALREADY_MEMBER",
        message="이미 스터디 멤버입니다.",
        status_code=400
    )

    STUDY_NOT_MEMBER = ErrorCodeInfo(
        code="STUDY_NOT_MEMBER",
        message="스터디 멤버가 아닙니다.",
        status_code=403
    )

    STUDY_OWNER_CANNOT_LEAVE = ErrorCodeInfo(
        code="STUDY_OWNER_CANNOT_LEAVE",
        message="스터디 방장은 탈퇴할 수 없습니다.",
        status_code=400
    )

    STUDY_OWNER_ONLY = ErrorCodeInfo(
        code="STUDY_OWNER_ONLY",
        message="스터디 방장만 수행할 수 있는 작업입니다.",
        status_code=403
    )

    CANNOT_KICK_OWNER = ErrorCodeInfo(
        code="CANNOT_KICK_OWNER",
        message="방장은 강퇴할 수 없습니다.",
        status_code=400
    )

    INVITATION_NOT_FOUND = ErrorCodeInfo(
        code="INVITATION_NOT_FOUND",
        message="초대를 찾을 수 없습니다.",
        status_code=404
    )

    INVITATION_ALREADY_SENT = ErrorCodeInfo(
        code="INVITATION_ALREADY_SENT",
        message="이미 초대를 보낸 유저입니다.",
        status_code=400
    )

    INVITATION_ALREADY_RESPONDED = ErrorCodeInfo(
        code="INVITATION_ALREADY_RESPONDED",
        message="이미 응답한 초대입니다.",
        status_code=400
    )

    INVITATION_NOT_FOR_ME = ErrorCodeInfo(
        code="INVITATION_NOT_FOR_ME",
        message="본인에게 온 초대가 아닙니다.",
        status_code=403
    )

    APPLICATION_NOT_FOUND = ErrorCodeInfo(
        code="APPLICATION_NOT_FOUND",
        message="가입 신청을 찾을 수 없습니다.",
        status_code=404
    )

    APPLICATION_ALREADY_SENT = ErrorCodeInfo(
        code="APPLICATION_ALREADY_SENT",
        message="이미 가입 신청을 보냈습니다.",
        status_code=400
    )

    APPLICATION_ALREADY_RESPONDED = ErrorCodeInfo(
        code="APPLICATION_ALREADY_RESPONDED",
        message="이미 처리된 가입 신청입니다.",
        status_code=400
    )

    STUDY_PROBLEM_NOT_FOUND = ErrorCodeInfo(
        code="STUDY_PROBLEM_NOT_FOUND",
        message="스터디 풀문제를 찾을 수 없습니다.",
        status_code=404
    )

    STUDY_PROBLEM_INVALID_TARGETS = ErrorCodeInfo(
        code="STUDY_PROBLEM_INVALID_TARGETS",
        message="유효하지 않은 대상 멤버가 포함되어 있습니다.",
        status_code=400
    )

    NOTICE_NOT_FOUND = ErrorCodeInfo(
        code="NOTICE_NOT_FOUND",
        message="알림을 찾을 수 없습니다.",
        status_code=404
    )

    NOTICE_NOT_FOR_ME = ErrorCodeInfo(
        code="NOTICE_NOT_FOR_ME",
        message="본인의 알림이 아닙니다.",
        status_code=403
    )