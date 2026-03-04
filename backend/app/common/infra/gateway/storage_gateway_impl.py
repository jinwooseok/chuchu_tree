import logging
import uuid
from datetime import timedelta
from io import BytesIO
from typing import override

from app.common.domain.gateway.storage_gateway import StorageGateway
from app.common.infra.client.storage_client import StorageClient
from app.config.settings import get_settings
from app.core.error_codes import ErrorCode
from app.core.exception import APIException

logger = logging.getLogger()


class S3StorageGatewayImpl(StorageGateway):
    """S3 호환 스토리지 게이트웨이 구현체 (RustFS / MinIO / S3)

    모든 경로에 {environment}/ prefix를 자동으로 추가합니다.
    외부에서는 환경 prefix 없이 순수 경로만 사용합니다.
    e.g. 외부: "chat/attachments/file.jpg" → 내부: "local/chat/attachments/file.jpg"
    """

    def __init__(self, storage_client: StorageClient):
        self.storage_client = storage_client
        settings = get_settings()
        self.bucket_name = settings.STORAGE_BUCKET_NAME
        self.environment = settings.ENVIRONMENT
        self.storage_endpoint = settings.STORAGE_ENDPOINT
        self.storage_public_url = settings.STORAGE_PUBLIC_URL

    def _to_object_key(self, path: str) -> str:
        """외부 경로 → S3 object key (환경 prefix 추가)"""
        return f"{self.environment}/{path}"

    @override
    async def upload_file(
        self,
        file_content: bytes,
        file_name: str,
        content_type: str,
        path_prefix: str = ""
    ) -> tuple[str, str]:
        """파일 업로드

        Returns:
            (file_path, safe_filename) - file_path는 환경 prefix 미포함
        """
        try:
            name_parts = file_name.rsplit('.', 1)
            extension = name_parts[1] if len(name_parts) == 2 else ''

            unique_id = uuid.uuid4().hex[:12]
            safe_filename = f"{unique_id}.{extension}" if extension else unique_id

            file_stream = BytesIO(file_content)
            relative_path = f"{path_prefix}{safe_filename}"
            object_key = self._to_object_key(relative_path)

            self.storage_client.create_bucket_if_not_exists(self.bucket_name)

            upload_success = await self.storage_client.upload_file(
                bucket_name=self.bucket_name,
                object_name=object_key,
                file_data=file_stream,
                content_type=content_type
            )

            if not upload_success:
                raise APIException(ErrorCode.INTERNAL_SERVER_ERROR)

            logger.info("파일 업로드 성공: %s", object_key)
            return relative_path, safe_filename

        except Exception as e:
            logger.error("파일 업로드 중 오류 발생: %s", e)
            raise APIException(ErrorCode.INTERNAL_SERVER_ERROR) from e

    @override
    async def delete_file(self, file_path: str) -> bool:
        """파일 삭제 (file_path는 환경 prefix 미포함)"""
        try:
            object_key = self._to_object_key(file_path)
            delete_success = self.storage_client.delete_file(
                bucket_name=self.bucket_name,
                object_name=object_key
            )

            if delete_success:
                logger.info("파일 삭제 성공: %s", object_key)
            else:
                logger.warning("파일 삭제 실패: %s", object_key)

            return delete_success

        except Exception as e:  # pylint:disable=broad-exception-caught
            logger.error("파일 삭제 중 오류 발생: %s", e)
            return False

    @override
    async def download_file(self, file_path: str) -> bytes | None:
        """파일 다운로드 (file_path는 환경 prefix 미포함)"""
        try:
            object_key = self._to_object_key(file_path)
            data = self.storage_client.download_file(
                bucket_name=self.bucket_name,
                object_name=object_key
            )
            return data
        except Exception as e:  # pylint:disable=broad-exception-caught
            logger.error("파일 다운로드 중 오류 발생: %s", e)
            return None

    @override
    async def generate_presigned_url(self, file_name: str, expiry_seconds: int = 3600) -> str | None:
        """Presigned URL 생성 (file_name은 환경 prefix 미포함, 도메인을 공개 URL로 치환)"""
        try:
            object_key = self._to_object_key(file_name)
            expires = timedelta(seconds=expiry_seconds)

            presigned_url = self.storage_client.get_file_url(
                bucket_name=self.bucket_name,
                object_name=object_key,
                expires=expires
            )

            if presigned_url:
                presigned_url = presigned_url.replace(
                    f"http://{self.storage_endpoint}",
                    self.storage_public_url
                )

            return presigned_url

        except Exception as e:  # pylint:disable=broad-exception-caught
            logger.debug("사인된 URL 생성 중 오류 발생: %s", e)
            return None
