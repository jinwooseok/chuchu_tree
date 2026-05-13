import re
from app.core.error_codes import ErrorCode
from app.core.exception import APIException


class PasswordValidator:
    """
    비밀번호 복잡도 검증 도메인 서비스

    비밀번호 보안 정책:
    - 최소 8자 이상
    - 영문자 포함 (대소문자 중 하나)
    - 숫자 포함
    - 특수문자 포함 (!@#$%^&*(),.?":{}|<>)
    """

    @staticmethod
    def validate_password_complexity(password: str) -> None:
        """
        비밀번호 복잡도 검증

        Args:
            password: 검증할 비밀번호

        Raises:
            APIException: 비밀번호가 정책을 만족하지 않을 때
        """
        if not password or len(password) < 8:
            raise APIException(
                ErrorCode.INVALID_PASSWORD_FORMAT,
                "비밀번호는 8자 이상이어야 합니다."
            )

        if not re.search(r'[a-zA-Z]', password):
            raise APIException(
                ErrorCode.INVALID_PASSWORD_FORMAT,
                "비밀번호는 영문자를 포함해야 합니다."
            )

        if not re.search(r'\d', password):
            raise APIException(
                ErrorCode.INVALID_PASSWORD_FORMAT,
                "비밀번호는 숫자를 포함해야 합니다."
            )

        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise APIException(
                ErrorCode.INVALID_PASSWORD_FORMAT,
                "비밀번호는 특수문자를 포함해야 합니다."
            )
