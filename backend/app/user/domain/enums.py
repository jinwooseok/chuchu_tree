from enum import Enum


class Provider(str, Enum):
    KAKAO = "KAKAO"
    NAVER = "NAVER"
    GOOGLE = "GOOGLE"
    NONE = "NONE"