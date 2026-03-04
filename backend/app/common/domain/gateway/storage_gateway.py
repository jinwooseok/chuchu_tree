"""Storage Gateway Interface"""
from abc import ABC, abstractmethod


class StorageGateway(ABC):
    """파일 저장소 접근을 위한 Gateway 인터페이스"""

    @abstractmethod
    async def upload_file(
        self,
        file_content: bytes,
        file_name: str,
        content_type: str,
        path_prefix: str = ""
    ) -> tuple[str, str]:
        """파일 업로드

        Args:
            file_content: 파일 바이너리 데이터
            file_name: 원본 파일명
            content_type: MIME 타입
            path_prefix: 저장 경로 접두사 (e.g., "documents/")

        Returns:
            (file_path, safe_filename) 튜플
        """

    @abstractmethod
    async def generate_presigned_url(self, file_name: str, expiry_seconds: int = 3600) -> str | None:
        """Presigned URL 생성

        Args:
            file_name: 파일명 (S3 key)
            expiry_seconds: 만료 시간 (초, 기본 1시간)

        Returns:
            서명된 다운로드 URL
        """

    @abstractmethod
    async def delete_file(self, file_path: str) -> bool:
        """파일 삭제

        Args:
            file_path: 파일 경로

        Returns:
            삭제 성공 여부
        """

    @abstractmethod
    async def download_file(self, file_path: str) -> bytes | None:
        """파일 다운로드

        Args:
            file_path: 파일 경로

        Returns:
            파일 바이너리 데이터 또는 None
        """
