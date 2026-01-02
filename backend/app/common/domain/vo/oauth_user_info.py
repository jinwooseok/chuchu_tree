from dataclasses import dataclass
from app.common.domain.enums import Provider

@dataclass(frozen=True)
class OAuthUserInfo:
    """OAuth 사용자 정보 Value Object (공통)"""

    provider: Provider
    provider_user_id: str
    nickname: str | None
    profile_image_url: str | None

@dataclass(frozen=True)
class NaverUserInfo(OAuthUserInfo):
    """네이버 사용자 정보 Value Object"""

    provider: Provider

    @classmethod
    def from_api_response(cls, response: dict) -> "NaverUserInfo":
        """
        네이버 API 응답을 NaverUserInfo 객체로 변환

        네이버 응답 형식:
        {
            "resultcode": "00",
            "message": "success",
            "response": {
                "id": "123456789",
                "nickname": "홍길동",
                "profile_image": "https://..."
            }
        }
        """
        user_data = response.get("response", {})

        return cls(
            provider_user_id=user_data.get("id", ""),
            nickname=user_data.get("nickname"),
            profile_image_url=user_data.get("profile_image")
        )

@dataclass(frozen=True)
class KakaoUserInfo(OAuthUserInfo):
    """카카오 사용자 정보 Value Object"""

    provider: Provider

    @classmethod
    def from_api_response(cls, response: dict) -> "KakaoUserInfo":
        """
        카카오 API 응답을 KakaoUserInfo 객체로 변환

        카카오 응답 형식 (scope: profile_nickname):
        {
            "id": 123456789,
            "kakao_account": {
                "profile": {
                    "nickname": "홍길동",
                    "profile_image_url": "https://..."
                }
            }
        }
        """
        kakao_account = response.get("kakao_account", {})
        profile = kakao_account.get("profile", {})

        return cls(
            provider_user_id=str(response.get("id", "")),
            nickname=profile.get("nickname"),
            profile_image_url=profile.get("profile_image_url")
        )
