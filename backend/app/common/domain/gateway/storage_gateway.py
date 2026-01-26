from abc import ABC, abstractmethod

class StorageGateway(ABC):
    """파일 저장소 게이트웨이 인터페이스"""
    
    @abstractmethod
    async def upload_file(self, bucket_name: str, prefix: str, file_content: bytes, file_name: str, content_type: str) -> tuple[str, str]:
        """
        파일 업로드
        
        Args:
            bucket_name: 버킷명
            file_content: 파일 내용 (bytes)
            file_name: 파일명
            content_type: MIME 타입
            
        Returns:
            업로드된 파일의 URL
        """
        pass
    
    @abstractmethod
    def delete_file(self, bucket_name: str, file_name: str) -> bool:
        """
        파일 삭제
        
        Args:
            bucket_name: 버킷명
            file_name: 파일명
            
        Returns:
            삭제 성공 여부
        """
        pass
    
    @abstractmethod
    def get_file_url(self, bucket_name: str, file_name: str) -> str:
        """
        파일 접근 URL 생성
        
        Args:
            bucket_name: 버킷명
            file_name: 파일명
            
        Returns:
            파일 접근 URL
        """
        pass
    
    @abstractmethod
    def generate_presigned_url(self, bucket_name: str, file_name: str, expiry_seconds: int = 3600) -> str|None:
        """
        사인된 URL 생성 (추후 권한 확인용)
        
        Args:
            bucket_name: 버킷명
            file_name: 파일명
            expiry_seconds: 만료 시간 (초)
            
        Returns:
            사인된 URL
        """
        pass

    @abstractmethod
    def _determine_file_type(self, file_name: str, mime_type: str) -> str:
        """파일 타입 결정"""
        pass