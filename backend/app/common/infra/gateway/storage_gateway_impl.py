import logging
import os
from datetime import timedelta
from io import BytesIO
from typing import Optional, override

from app.common.domain.gateway.storage_gateway import StorageGateway
from app.common.infra.client.storage_client import StorageClient
from app.core.error_codes import ErrorCode
from app.core.exception import APIException

logger = logging.getLogger()


class StorageGatewayImpl(StorageGateway):
    """MinIO 기반 스토리지 게이트웨이 구현체"""
    
    def __init__(self, storage_client: StorageClient):
        self.storage_client = storage_client
    
    @override
    def _determine_file_type(self, file_name: str, mime_type: str) -> str:
        """파일 타입 결정"""
        # 이미지 파일 확장자 및 MIME 타입 확인
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
        image_mimes = {'image/jpeg', 'image/png', 'image/gif', 'image/bmp', 'image/webp'}
        
        file_extension = os.path.splitext(file_name.lower())[1]
        
        if file_extension in image_extensions or mime_type in image_mimes:
            return 'image'
        else:
            return 'document'
    
    @override
    async def upload_file(self, bucket_name: str, prefix: str, file_content: bytes, file_name: str, content_type: str) -> tuple[str, str]:
        """
        파일 업로드

        Args:
            bucket_name: 버킷명
            prefix: 접두사
            file_content: 파일 내용 (bytes)
            file_name: 파일명
            content_type: MIME 타입

        Returns:
            업로드된 파일의 URL
        """
        try:
            import re
            import uuid

            # 파일명에서 확장자 분리
            name_parts = file_name.rsplit('.', 1)
            if len(name_parts) == 2:
                base_name, extension = name_parts
            else:
                base_name = file_name
                extension = ''

            # UUID 기반 고유 파일명 생성 (한글/특수문자 문제 회피)
            unique_id = uuid.uuid4().hex[:12]
            if extension:
                safe_filename = f"{unique_id}.{extension}"
            else:
                safe_filename = unique_id
            
            # BytesIO 스트림 생성
            file_stream = BytesIO(file_content)
            
            # 버킷 생성 (존재하지 않는 경우)
            self.storage_client.create_bucket_if_not_exists(bucket_name)
            
            # 파일 업로드
            upload_success = await self.storage_client.upload_file(
                bucket_name=bucket_name,
                object_name=f"{prefix}{safe_filename}",
                file_data=file_stream,
                content_type=content_type
            )
            
            if not upload_success:
                raise APIException(ErrorCode.INTERNAL_SERVER_ERROR)
            
            # 업로드된 파일의 경로 반환 (DB 저장용)
            file_path = f"{prefix}{safe_filename}"
            logger.info(f"파일 업로드 성공: {safe_filename}")
            return file_path, safe_filename
            
        except Exception as e:
            logger.error(f"파일 업로드 중 오류 발생: {str(e)}")
            raise APIException(ErrorCode.INTERNAL_SERVER_ERROR)
    @override
    def delete_file(self, bucket_name: str, file_name: str) -> bool:
        """
        파일 삭제
        
        Args:
            bucket_name: 버킷명
            file_name: 파일명
            
        Returns:
            삭제 성공 여부
        """
        try:
            # 파일 삭제
            delete_success = self.storage_client.delete_file(
                bucket_name=bucket_name,
                object_name=file_name
            )
            
            if delete_success:
                logger.info(f"파일 삭제 성공: {file_name}")
            else:
                logger.warning(f"파일 삭제 실패: {file_name}")
                
            return delete_success
            
        except Exception as e:
            logger.error(f"파일 삭제 중 오류 발생: {str(e)}")
            return False
    
    @override
    def get_file_url(self, bucket_name: str, file_name: str) -> str:
        """
        파일 접근 URL 생성
        
        Args:
            bucket_name: 버킷명
            file_name: 파일명
            
        Returns:
            파일 접근 URL
        """
        try:
            # 영구적인 URL 생성
            url = self.storage_client.get_file_url(
                bucket_name=bucket_name,
                object_name=file_name
            )
            
            if not url:
                raise APIException(ErrorCode.INTERNAL_SERVER_ERROR)
                
            return url
            
        except Exception as e:
            logger.error(f"파일 URL 생성 중 오류 발생: {str(e)}")
            raise APIException(ErrorCode.INTERNAL_SERVER_ERROR)
    
    @override
    def generate_presigned_url(self, bucket_name: str, file_name: str, expiry_seconds: int = 3600) -> Optional[str]:
        """
        사인된 URL 생성 (추후 권한 확인용)
        
        Args:
            bucket_name: 버킷명
            file_name: 파일명
            expiry_seconds: 만료 시간 (초)
            
        Returns:
            사인된 URL
        """
        try:
            # timedelta로 변환
            expires = timedelta(seconds=expiry_seconds)
            
            # 사인된 URL 생성
            presigned_url = self.storage_client.get_file_url(
                bucket_name=bucket_name,
                object_name=file_name,
                expires=expires
            )
            
            return presigned_url
            
        except Exception as e:
            logger.debug(f"사인된 URL 생성 중 오류 발생: {str(e)}")
            return None