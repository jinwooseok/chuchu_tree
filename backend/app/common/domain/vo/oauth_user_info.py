from dataclasses import dataclass
from app.common.domain.enums import Provider

@dataclass(frozen=True)
class OAuthUserInfo:
    """OAuth 사용자 정보 Value Object (공통)"""

    provider_id: str
    nickname: str | None
    profile_image_url: str | None
    provider: Provider

@dataclass(frozen=True)
class NaverUserInfo(OAuthUserInfo):
    """네이버 사용자 정보 Value Object"""

    provider: Provider = Provider.NAVER

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
            provider_id=user_data.get("id", ""),
            nickname=user_data.get("nickname"),
            profile_image_url=user_data.get("profile_image")
        )

@dataclass(frozen=True)
class KakaoUserInfo(OAuthUserInfo):
    """카카오 사용자 정보 Value Object"""

    provider: Provider = Provider.KAKAO

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
            provider_id=str(response.get("id", "")),
            nickname=profile.get("nickname"),
            profile_image_url=profile.get("profile_image_url")
        )

@dataclass(frozen=True)
class GoogleUserInfo(OAuthUserInfo):
    """구글 사용자 정보 Value Object"""

    provider: Provider = Provider.GOOGLE

    @classmethod
    def from_api_response(cls, response: dict) -> "GoogleUserInfo":
        """
        구글 API 응답을 GoogleUserInfo 객체로 변환

        구글 응답 형식:
        {
            "sub": "1234567890",
            "name": "홍길동",
            "picture": "https://..."
        }
        """
        return cls(
            provider_id=response.get("sub", ""),
            nickname=response.get("name"),
            profile_image_url=response.get("picture")
        )

@dataclass(frozen=True)
class GitHubUserInfo(OAuthUserInfo):
    """깃허브 사용자 정보 Value Object"""

    provider: Provider = Provider.GITHUB

    @classmethod
    def from_api_response(cls, response: dict) -> "GitHubUserInfo":
        """
        깃허브 API 응답을 GitHubUserInfo 객체로 변환

        깃허브 응답 형식:
        {
            "id": 1234567,
            "login": "username",
            "name": "홍길동",
            "avatar_url": "https://..."
        }
        """
        return cls(
            provider_id=str(response.get("id", "")),
            nickname=response.get("name") or response.get("login"),
            profile_image_url=response.get("avatar_url")
        )
