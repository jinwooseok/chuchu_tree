
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