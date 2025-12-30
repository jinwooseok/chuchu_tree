import logging
from app.core.api_response import ApiResponse
from app.core.error_codes import ErrorCode

logger = logging.getLogger()
class APIException(Exception):
    def __init__(
        self,
        error_code: ErrorCode,
        message: str|None = None
    ):
        self.status_code = error_code.value.status_code
        self.error_code = error_code.value.code
        self.message = message if message else error_code.value.message
        super().__init__(self.message)

# 기본 HTTPException 핸들러
async def startlette_http_exception_handler(request, exc):
    logger.error(f"HTTP 에러: {exc.detail}")
    return ApiResponse(
        status_code=exc.status_code,
        error_code="HTTP_ERROR",
        error_message=str(exc.detail)
    )

# 기본 HTTPException 핸들러
async def http_exception_handler(request, exc):
    logger.error(f"HTTP 에러: {exc.detail}")
    return ApiResponse(
        status_code=exc.status_code,
        error_code="HTTP_ERROR",
        error_message=str(exc.detail)
    )

# 요청 유효성 검증 에러 핸들러
async def validation_exception_handler(request, exc):
    logger.error(f"유효성 검증 에러: {exc}")

    # 유효성 검증 오류 상세 정보 처리
    error_details = exc.errors()

    if error_details and len(error_details) > 0:
        first_error = error_details[0]
        error_type = first_error.get('type', '')

        # 에러 타입에 따라 적절한 ErrorCode로 매핑
        from core.error_codes import ErrorCode

        # missing: 필수 필드 누락
        if error_type == 'missing':
            error_code = ErrorCode.MISSING_REQUIRED_FIELD
        # string_too_short: 입력값이 너무 짧음
        elif error_type == 'string_too_short':
            error_code = ErrorCode.INPUT_TOO_SHORT
        # int_parsing, float_parsing 등: 타입 변환 실패
        elif 'parsing' in error_type or 'type' in error_type:
            error_code = ErrorCode.INVALID_INPUT_TYPE
        # value_error: 값 형식 에러 (이메일 등은 field_validator에서 처리됨)
        elif error_type == 'value_error':
            error_code = ErrorCode.INVALID_INPUT_TYPE
        # 기타 validation 에러
        else:
            error_code = ErrorCode.INVALID_REQUEST

        return ApiResponse(
            status_code=error_code.value.status_code,
            error_code=error_code.value.code,
            error_message=error_code.value.message
        )

    # 에러 정보가 없는 경우 기본 에러
    from core.error_codes import ErrorCode
    return ApiResponse(
        status_code=400,
        error_code=ErrorCode.INVALID_REQUEST.value.code,
        error_message=ErrorCode.INVALID_REQUEST.value.message
    )

async def custom_exception_handler(request, exc):
    # isinstance로 타입 체크
    if isinstance(exc, APIException):
        if exc.error_code == "DATABASE_ERROR":
            logger.error(f"데이터베이스 오류: {exc}", exc_info=True)
        else:
            logger.error(f"API 오류: {exc}", exc_info=True)
        return ApiResponse(
            status_code=exc.status_code,
            error_code=exc.error_code,
            error_message=exc.message
        )
    else:
        # APIException이 아닌 경우 일반 처리
        logger.error(f"예상치 못한 에러: {str(exc)}")
        return ApiResponse(
            status_code=500,
            error_code="INTERNAL_SERVER_ERROR",
            error_message="서버 내부 오류가 발생했습니다"
        )