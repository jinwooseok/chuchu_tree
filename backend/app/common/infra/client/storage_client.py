from abc import ABC, abstractmethod
import os
from typing import BinaryIO, Any
from datetime import timedelta
import logging

import boto3
from botocore.config import Config as BotoConfig
from botocore.exceptions import ClientError
from fastapi import HTTPException

from app.config.settings import get_settings


logger = logging.getLogger(__name__)
settings = get_settings()


class StorageClient(ABC):
    @abstractmethod
    def check_bucket_exists(self, bucket_name: str) -> bool:
        pass

    @abstractmethod
    def create_bucket_if_not_exists(self, bucket_name: str) -> bool:
        pass

    @abstractmethod
    async def upload_file(
            self,
            bucket_name: str,
            object_name: str,
            file_data: BinaryIO,
            content_type: str | None = None,
            encoding: str | None = "utf-8"
    ) -> bool:
        pass

    @abstractmethod
    def get_file(self, bucket_name: str, object_name: str) -> bytes | None:
        pass

    @abstractmethod
    def get_metadata(self, bucket_name: str, object_name: str) -> dict[str, Any] | None:
        pass

    @abstractmethod
    def get_file_url(self, bucket_name: str, object_name: str, expires: timedelta = timedelta(hours=1)) -> str | None:
        pass

    @abstractmethod
    async def save_object(self, bucket_name: str, object_name: str, data: BinaryIO, content_type: str, encoding: str) -> str | None:
        pass

    @abstractmethod
    def delete_file(self, bucket_name: str, object_name: str) -> bool:
        pass

    @abstractmethod
    def download_file(self, bucket_name: str, object_name: str) -> bytes | None:
        pass


class S3Client(StorageClient):
    def __init__(self):
        """boto3 S3 클라이언트 초기화 (S3 호환 스토리지용)"""
        try:
            endpoint = settings.STORAGE_ENDPOINT
            endpoint_url = endpoint if endpoint.startswith(("http://", "https://")) else f"http://{endpoint}"
            print(settings.STORAGE_ACCESS_KEY)
            print(settings.STORAGE_SECRET_KEY)
            self.client = boto3.client(
                "s3",
                endpoint_url=endpoint_url,
                aws_access_key_id=settings.STORAGE_ACCESS_KEY,
                aws_secret_access_key=settings.STORAGE_SECRET_KEY,
                config=BotoConfig(signature_version="s3v4"),
                region_name="us-east-1",
            )
            logger.info("S3 클라이언트가 성공적으로 초기화되었습니다. (endpoint: %s)", endpoint_url)
        except Exception as e:
            logger.error("S3 클라이언트 초기화 실패: %s", e)
            raise HTTPException(status_code=500, detail="스토리지 서비스 연결 실패") from e

    def check_bucket_exists(self, bucket_name: str) -> bool:
        """지정된 버킷이 존재하는지 확인"""
        try:
            self.client.head_bucket(Bucket=bucket_name)
            return True
        except ClientError:
            return False

    def create_bucket_if_not_exists(self, bucket_name: str) -> bool:
        """버킷이 존재하지 않으면 생성"""
        if self.check_bucket_exists(bucket_name):
            return True
        try:
            self.client.create_bucket(Bucket=bucket_name)
            logger.info("버킷 '%s'이 성공적으로 생성되었습니다.", bucket_name)
            return True
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "")
            # 이미 존재하거나 서버가 생성 API를 지원하지 않는 경우 계속 진행
            if error_code in ("BucketAlreadyExists", "BucketAlreadyOwnedByYou", "404"):
                logger.warning("버킷 '%s' 생성 API 미지원 또는 이미 존재 (code=%s), 업로드를 계속합니다.", bucket_name, error_code)
                return True
            logger.error("버킷 '%s' 생성 중 오류: %s", bucket_name, e)
            return False

    async def upload_file(
            self,
            bucket_name: str,
            object_name: str,
            file_data: BinaryIO,
            content_type: str | None = None,
            encoding: str | None = "utf-8"
    ) -> bool:
        """파일을 스토리지에 업로드"""
        try:
            self.create_bucket_if_not_exists(bucket_name)

            file_data.seek(0, os.SEEK_END)
            file_size = file_data.tell()
            file_data.seek(0)

            # upload_fileobj는 Content-Length 없이 chunked 전송해 413 유발
            # put_object로 ContentLength를 명시해 전송
            self.client.put_object(
                Bucket=bucket_name,
                Key=object_name,
                Body=file_data,
                ContentLength=file_size,
                ContentType=content_type or "application/octet-stream",
            )
            return True
        except ClientError as e:
            logger.error("파일 '%s' 업로드 중 오류: %s", object_name, e)
            return False

    def get_file(self, bucket_name: str, object_name: str) -> bytes | None:
        """스토리지에서 파일 다운로드"""
        try:
            response = self.client.get_object(Bucket=bucket_name, Key=object_name)
            data = response["Body"].read()
            response["Body"].close()
            return data
        except ClientError:
            return None

    def download_file(self, bucket_name: str, object_name: str) -> bytes | None:
        """파일 다운로드 (get_file 래핑)"""
        return self.get_file(bucket_name, object_name)

    def get_metadata(self, bucket_name: str, object_name: str) -> dict[str, Any] | None:
        try:
            response = self.client.head_object(Bucket=bucket_name, Key=object_name)
            return {
                'size': response.get('ContentLength'),
                'content_type': response.get('ContentType'),
                'etag': response.get('ETag'),
                'last_modified': response.get('LastModified'),
                'metadata': response.get('Metadata', {}),
                'version_id': response.get('VersionId'),
            }
        except ClientError:
            return None

    def get_file_url(self, bucket_name: str, object_name: str, expires: timedelta = timedelta(hours=1)) -> str | None:
        """파일에 대한 임시 URL 생성"""
        try:
            url = self.client.generate_presigned_url(
                "get_object",
                Params={"Bucket": bucket_name, "Key": object_name},
                ExpiresIn=int(expires.total_seconds()),
            )
            return url
        except ClientError as e:
            logger.error("파일 '%s'의 URL 생성 중 오류: %s", object_name, e)
            return None

    def delete_file(self, bucket_name: str, object_name: str) -> bool:
        """스토리지에서 파일 삭제"""
        try:
            self.client.delete_object(Bucket=bucket_name, Key=object_name)
            logger.info("파일 '%s'이 버킷 '%s'에서 성공적으로 삭제되었습니다.", object_name, bucket_name)
            return True
        except ClientError as e:
            logger.error("파일 '%s' 삭제 중 오류: %s", object_name, e)
            return False

    async def save_object(self, bucket_name: str, object_name: str, data: BinaryIO, content_type: str, encoding: str) -> str | None:
        """객체를 저장하고 생성된 etag를 반환"""
        try:
            data.seek(0, 2)
            size = data.tell()
            data.seek(0)

            if not self.check_bucket_exists(bucket_name):
                self.client.create_bucket(Bucket=bucket_name)

            self.client.upload_fileobj(
                Fileobj=data,
                Bucket=bucket_name,
                Key=object_name,
                ExtraArgs={
                    "ContentType": content_type,
                    "Metadata": {"encoding": encoding},
                },
            )

            # etag 조회
            response = self.client.head_object(Bucket=bucket_name, Key=object_name)
            return response.get("ETag")
        except ClientError as err:
            logger.error("S3 Error: %s", err)
            return None
        except Exception as err:
            logger.error("Error: %s", err)
            return None
