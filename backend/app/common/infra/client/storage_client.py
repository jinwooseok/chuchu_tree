from abc import ABC, abstractmethod
import hashlib
import hmac
import traceback
from urllib import parse
import requests
from minio import Minio
from minio.error import S3Error
from fastapi import HTTPException
from typing import Optional, BinaryIO, Any, Dict
from datetime import datetime, timedelta, timezone
import logging
import os

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
            content_type: Optional[str] = None,
            encoding: Optional[str] = "utf-8"
    ) -> bool:
        pass
    
    @abstractmethod
    def get_file(self, bucket_name: str, object_name: str) -> Optional[bytes]:
        pass
    
    @abstractmethod
    def get_metadata(self, bucket_name: str, object_name: str) -> Optional[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def get_file_url(self, bucket_name: str, object_name: str, expires=timedelta(hours=1)) -> Optional[str]:
        pass
    
    @abstractmethod
    async def save_object(self, bucket_name: str, object_name: str, data: BinaryIO, content_type: str, encoding: str) -> \
            Optional[str]:
        pass
    
    @abstractmethod
    def delete_file(self, bucket_name: str, object_name: str) -> bool:
        pass
    

class MinioClient:
    def __init__(self):
        """MinIO 클라이언트 초기화"""
        try:
            self.client = Minio(
                endpoint=settings.STORAGE_ENDPOINT,
                access_key=settings.STORAGE_ACCESS_KEY,
                secret_key=settings.STORAGE_SECRET_KEY,
                secure=False
            )
            logger.info("MinIO 클라이언트가 성공적으로 초기화되었습니다.")
        except Exception as e:
            logger.error(f"MinIO 클라이언트 초기화 실패: {str(e)}")
            raise HTTPException(status_code=500, detail="스토리지 서비스 연결 실패")

    def check_bucket_exists(self, bucket_name: str) -> bool:
        """지정된 버킷이 존재하는지 확인"""
        try:
            return self.client.bucket_exists(bucket_name)
        except S3Error as e:
            logger.error(f"버킷 존재 여부 확인 중 오류: {str(e)}")
            return False

    def create_bucket_if_not_exists(self, bucket_name: str) -> bool:
        """버킷이 존재하지 않으면 생성"""
        try:
            if not self.check_bucket_exists(bucket_name):
                self.client.make_bucket(bucket_name)
                logger.info(f"버킷 '{bucket_name}'이 성공적으로 생성되었습니다.")
            return True
        except S3Error as e:
            logger.error(f"버킷 '{bucket_name}' 생성 중 오류: {str(e)}")
            return False

    async def upload_file(
            self,
            bucket_name: str,
            object_name: str,
            file_data: BinaryIO,
            content_type: str
    ) -> bool:
        """파일을 MinIO에 업로드"""
        try:
            # 버킷이 존재하는지 확인하고 없으면 생성
            self.create_bucket_if_not_exists(bucket_name)

            # 파일 크기 계산
            file_data.seek(0, os.SEEK_END)
            file_size = file_data.tell()

            # 디버깅: 파일 데이터와 크기 출력
            file_data.seek(0)  # 포인터를 다시 처음으로 이동

            # 파일 업로드
            self.client.put_object(
                bucket_name=bucket_name,
                object_name=object_name,
                data=file_data,
                length=file_size,
                content_type=content_type
            )
            # file_data.close() 호출을 제거 - 호출자가 파일을 닫도록 함

            # 업로드 후 파일이 실제로 존재하는지 확인
            try:
                stat = self.client.stat_object(bucket_name, object_name)
                return True
            except Exception as stat_err:
                return False
        except S3Error as e:
            logger.error(f"파일 '{object_name}' 업로드 중 오류: {str(e)}")
            return False

    def get_file(self, bucket_name: str, object_name: str) -> Optional[bytes]:
        """MinIO에서 파일 다운로드"""
        try:
            response = self.client.get_object(bucket_name, object_name)
            data = response.read()
            response.release_conn()
            return data
        except S3Error as e:
            return None

    def get_metadata(self, bucket_name: str, object_name: str) -> Optional[Dict[str, Any]]:
        try:
            obj_info = self.client.stat_object(bucket_name, object_name)

            metadata = {
                'size': obj_info.size,
                'content_type': obj_info.content_type,
                'etag': obj_info.etag,
                'last_modified': obj_info.last_modified,
                'metadata': obj_info.metadata,
                'version_id': obj_info.version_id
            }

            return metadata
        except S3Error as e:
            return None

    def get_file_url(self, bucket_name: str, object_name: str, expires=timedelta(hours=1)) -> Optional[str]:
        """파일에 대한 임시 URL 생성"""
        try:
            # 파일이 실제로 존재하는지 확인
            try:
                stat = self.client.stat_object(bucket_name, object_name)
                print(f"디버깅: URL 생성 전 파일 상태: {stat.__dict__}")
            except Exception as stat_err:
                print(f"디버깅: URL 생성 전 파일이 존재하지 않음: {str(stat_err)}")

            url = self.client.presigned_get_object(
                bucket_name=bucket_name,
                object_name=object_name,
                expires=expires
            )
            print(f"디버깅: 생성된 URL: {url}")

            return url
        except S3Error as e:
            logger.error(f"파일 '{object_name}'의 URL 생성 중 오류: {str(e)}")
            print(f"디버깅: URL 생성 중 오류: {str(e)}")
            return None

    def delete_file(self, bucket_name: str, object_name: str) -> bool:
        """MinIO에서 파일 삭제"""
        try:
            self.client.remove_object(bucket_name, object_name)
            logger.info(f"파일 '{object_name}'이 버킷 '{bucket_name}'에서 성공적으로 삭제되었습니다.")
            return True
        except S3Error as e:
            logger.error(f"파일 '{object_name}' 삭제 중 오류: {str(e)}")
            return False

    async def save_object(self, bucket_name: str, object_name: str, data: BinaryIO, content_type: str, encoding: str) -> \
            Optional[str]:
        """객체를 저장하고 생성된 etag를 반환합니다."""
        try:
            # 버퍼 크기 계산
            current_position = data.tell()
            data.seek(0, 2)  # 끝으로 이동
            size = data.tell()  # 크기 확인
            data.seek(0)  # 처음으로 돌아감

            logger.info(f"데이터 버퍼 크기: {size} 바이트")

            # 버킷이 없으면 생성
            if not self.client.bucket_exists(bucket_name):
                self.client.make_bucket(bucket_name)

            # 객체 업로드 (명시적 크기 지정)
            result = self.client.put_object(
                bucket_name=bucket_name,
                object_name=object_name,
                data=data,
                length=size,  # 명시적 크기 지정
                content_type=content_type,
                metadata={"encoding": encoding}
            )

        except S3Error as err:
            print(f"S3 Error: {err}")
            return None
        except Exception as err:
            print(f"Error: {err}")
            return None
        
class NCloudClient(StorageClient):
    """NCloud Object Storage 클라이언트 (AWS Signature V4 직접 구현)"""

    def __init__(self):
        """NCloud Object Storage 클라이언트 초기화"""
        try:
            # NCloud 설정
            self.region = settings.STORAGE_REGION or 'kr-standard'

            # endpoint 처리
            if settings.STORAGE_ENDPOINT:
                if settings.STORAGE_ENDPOINT.startswith('http://') or settings.STORAGE_ENDPOINT.startswith('https://'):
                    self.endpoint = settings.STORAGE_ENDPOINT
                    # https://kr.object.ncloudstorage.com -> kr.object.ncloudstorage.com
                    self.host = settings.STORAGE_ENDPOINT.replace('https://', '').replace('http://', '')
                else:
                    self.endpoint = f'https://{settings.STORAGE_ENDPOINT}'
                    self.host = settings.STORAGE_ENDPOINT
            else:
                raise ValueError("STORAGE_ENDPOINT가 설정되지 않았습니다.")

            self.access_key = settings.STORAGE_ACCESS_KEY
            self.secret_key = settings.STORAGE_SECRET_KEY

            # AWS Signature V4 설정
            self.payload_hash = 'UNSIGNED-PAYLOAD'
            self.hashing_algorithm = 'AWS4-HMAC-SHA256'
            self.service_name = 's3'
            self.request_type = 'aws4_request'
            self.time_format = '%Y%m%dT%H%M%SZ'
            self.date_format = '%Y%m%d'

            logger.info(f"NCloud Object Storage 클라이언트가 성공적으로 초기화되었습니다. endpoint: {self.endpoint}, region: {self.region}")
        except Exception as e:
            logger.error(f"NCloud Object Storage 클라이언트 초기화 실패: {str(e)}")
            raise Exception(f"스토리지 서비스 연결 실패: {str(e)}")

    def _get_hash(self, key, msg):
        """HMAC-SHA256 해시 생성"""
        return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()

    def _encode_path(self, path):
        """경로를 URL 인코딩 (AWS S3 방식)"""
        if path.startswith('/'):
            path_parts = path[1:].split('/')
            return '/' + '/'.join(parse.quote(part, safe='') for part in path_parts)
        else:
            path_parts = path.split('/')
            return '/'.join(parse.quote(part, safe='') for part in path_parts)

    def _create_signed_headers(self, headers):
        """서명된 헤더 문자열 생성"""
        signed_headers = []
        for k in sorted(headers):
            signed_headers.append('%s;' % k)
        return ''.join(signed_headers)[:-1]

    def _create_standardized_headers(self, headers):
        """표준화된 헤더 문자열 생성"""
        signed_headers = []
        for k in sorted(headers):
            signed_headers.append('%s:%s\n' % (k, headers[k]))
        return ''.join(signed_headers)

    def _create_standardized_query_parameters(self, request_parameters):
        """표준화된 쿼리 파라미터 문자열 생성"""
        standardized_query_parameters = []
        if request_parameters:
            for k in sorted(request_parameters):
                standardized_query_parameters.append('%s=%s' % (k, parse.quote(str(request_parameters[k]), safe='')))
            return '&'.join(standardized_query_parameters)
        else:
            return ''

    def _create_credential_scope(self, date_stamp):
        """인증 범위 생성"""
        return date_stamp + '/' + self.region + '/' + self.service_name + '/' + self.request_type

    def _create_canonical_request(self, http_method, request_path, request_parameters, headers):
        """정규 요청 생성"""
        encoded_path = self._encode_path(request_path)

        standardized_query_parameters = self._create_standardized_query_parameters(request_parameters)
        standardized_headers = self._create_standardized_headers(headers)
        signed_headers = self._create_signed_headers(headers)

        canonical_request = (http_method + '\n' +
                             encoded_path + '\n' +
                             standardized_query_parameters + '\n' +
                             standardized_headers + '\n' +
                             signed_headers + '\n' +
                             self.payload_hash)
        return canonical_request

    def _create_string_to_sign(self, time_stamp, credential_scope, canonical_request):
        """서명할 문자열 생성"""
        string_to_sign = (self.hashing_algorithm + '\n' +
                          time_stamp + '\n' +
                          credential_scope + '\n' +
                          hashlib.sha256(canonical_request.encode('utf-8')).hexdigest())
        return string_to_sign

    def _create_signature_key(self, date_stamp):
        """서명 키 생성"""
        key_date = self._get_hash(('AWS4' + self.secret_key).encode('utf-8'), date_stamp)
        key_string = self._get_hash(key_date, self.region)
        key_service = self._get_hash(key_string, self.service_name)
        key_signing = self._get_hash(key_service, self.request_type)
        return key_signing

    def _create_authorization_header(self, headers, signature_key, string_to_sign, credential_scope):
        """인증 헤더 생성"""
        signed_headers = self._create_signed_headers(headers)
        signature = hmac.new(signature_key, string_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()

        return (self.hashing_algorithm + ' ' +
                'Credential=' + self.access_key + '/' + credential_scope + ', ' +
                'SignedHeaders=' + signed_headers + ', ' +
                'Signature=' + signature)

    def _sign_request(self, http_method, request_path, headers, time, request_parameters=None):
        """요청에 서명 추가"""
        time_stamp = time.strftime(self.time_format)
        date_stamp = time.strftime(self.date_format)

        credential_scope = self._create_credential_scope(date_stamp)
        canonical_request = self._create_canonical_request(http_method, request_path, request_parameters, headers)
        string_to_sign = self._create_string_to_sign(time_stamp, credential_scope, canonical_request)
        signature_key = self._create_signature_key(date_stamp)

        headers['authorization'] = self._create_authorization_header(headers, signature_key, string_to_sign, credential_scope)

    def check_bucket_exists(self, bucket_name: str) -> bool:
        """지정된 버킷이 존재하는지 확인"""
        try:
            http_method = 'HEAD'
            request_path = f'/{bucket_name}'

            time = datetime.now()
            time_stamp = time.strftime(self.time_format)

            headers = {
                'x-amz-date': time_stamp,
                'x-amz-content-sha256': self.payload_hash,
                'host': self.host
            }

            self._sign_request(http_method, request_path, headers, time)

            request_url = self.endpoint + request_path
            r = requests.head(request_url, headers=headers)

            return r.status_code == 200
        except Exception as e:
            logger.error(f"버킷 존재 여부 확인 중 오류: {str(e)}")
            return False

    def create_bucket_if_not_exists(self, bucket_name: str) -> bool:
        """버킷이 존재하지 않으면 생성"""
        try:
            if self.check_bucket_exists(bucket_name):
                return True

            http_method = 'PUT'
            request_path = f'/{bucket_name}'

            time = datetime.now()
            time_stamp = time.strftime(self.time_format)

            headers = {
                'x-amz-date': time_stamp,
                'x-amz-content-sha256': self.payload_hash,
                'x-amz-acl': 'public-read',
                'host': self.host
            }

            self._sign_request(http_method, request_path, headers, time)

            request_url = self.endpoint + request_path
            r = requests.put(request_url, headers=headers)

            if r.status_code in [200, 409]:  # 409 = 이미 존재함
                logger.info(f"버킷 '{bucket_name}'이 성공적으로 생성되었습니다.")
                return True
            else:
                logger.error(f"버킷 '{bucket_name}' 생성 실패: {r.status_code} - {r.text}")
                return False
        except Exception as e:
            logger.error(f"버킷 '{bucket_name}' 생성 중 예외: {str(e)}")
            return False

    async def upload_file(
            self,
            bucket_name: str,
            object_name: str,
            file_data: BinaryIO,
            content_type: Optional[str] = None,
            encoding: Optional[str] = "utf-8"
    ) -> bool:
        """파일을 NCloud Object Storage에 업로드"""
        try:
            # 버킷이 존재하는지 확인하고 없으면 생성
            self.create_bucket_if_not_exists(bucket_name)

            # 파일 포인터를 처음으로 이동
            file_data.seek(0)
            content = file_data.read()

            http_method = 'PUT'
            request_path = f'/{bucket_name}/{object_name}'

            time = datetime.now()
            time_stamp = time.strftime(self.time_format)

            headers = {
                'x-amz-date': time_stamp,
                'x-amz-content-sha256': self.payload_hash,
                'x-amz-acl': 'public-read',
                'host': self.host
            }

            if content_type:
                headers['content-type'] = content_type

            self._sign_request(http_method, request_path, headers, time)

            # URL 인코딩된 request_path 생성 (실제 HTTP 요청용)
            encoded_request_path = self._encode_path(request_path)
            request_url = self.endpoint + encoded_request_path
            logger.info(f"Uploading to URL: {request_url}")

            r = requests.put(request_url, headers=headers, data=content)

            if r.status_code == 200:
                logger.info(f"파일 '{object_name}'이 버킷 '{bucket_name}'에 성공적으로 업로드되었습니다.")
                return True
            else:
                logger.error(f"파일 '{object_name}' 업로드 실패: {r.status_code} - {r.text}")
                return False
        except Exception as e:
            logger.error(f"파일 '{object_name}' 업로드 중 예외: {str(e)}")
            return False

    def get_file(self, bucket_name: str, object_name: str) -> Optional[bytes]:
        """NCloud Object Storage에서 파일 다운로드"""
        try:
            http_method = 'GET'
            request_path = f'/{bucket_name}/{object_name}'

            time = datetime.now()
            time_stamp = time.strftime(self.time_format)

            headers = {
                'x-amz-date': time_stamp,
                'x-amz-content-sha256': self.payload_hash,
                'host': self.host
            }

            self._sign_request(http_method, request_path, headers, time)

            # URL 인코딩된 request_path 생성
            encoded_request_path = self._encode_path(request_path)
            request_url = self.endpoint + encoded_request_path

            r = requests.get(request_url, headers=headers)

            if r.status_code == 200:
                return r.content
            else:
                logger.error(f"파일 '{object_name}' 다운로드 실패: {r.status_code}")
                return None
        except Exception as e:
            logger.error(f"파일 '{object_name}' 다운로드 중 예외: {str(e)}")
            return None

    def get_metadata(self, bucket_name: str, object_name: str) -> Optional[Dict[str, Any]]:
        """파일 메타데이터 조회"""
        try:
            http_method = 'HEAD'
            request_path = f'/{bucket_name}/{object_name}'

            time = datetime.now()
            time_stamp = time.strftime(self.time_format)

            headers = {
                'x-amz-date': time_stamp,
                'x-amz-content-sha256': self.payload_hash,
                'host': self.host
            }

            self._sign_request(http_method, request_path, headers, time)

            # URL 인코딩된 request_path 생성
            encoded_request_path = self._encode_path(request_path)
            request_url = self.endpoint + encoded_request_path

            r = requests.head(request_url, headers=headers)

            if r.status_code == 200:
                metadata = {
                    'size': r.headers.get('Content-Length'),
                    'content_type': r.headers.get('Content-Type'),
                    'etag': r.headers.get('ETag'),
                    'last_modified': r.headers.get('Last-Modified'),
                }
                return metadata
            else:
                logger.error(f"파일 '{object_name}' 메타데이터 조회 실패: {r.status_code}")
                return None
        except Exception as e:
            logger.error(f"파일 '{object_name}' 메타데이터 조회 중 예외: {str(e)}")
            return None

    def get_file_url(self, bucket_name: str, object_name: str, expires=timedelta(hours=1)) -> Optional[str]:
        """파일에 대한 임시 서명된 URL 생성 (Presigned URL)"""
        try:
            http_method = 'GET'
            request_path = f'/{bucket_name}/{object_name}'

            time = datetime.now()
            time_stamp = time.strftime(self.time_format)
            date_stamp = time.strftime(self.date_format)

            expires_in_seconds = int(expires.total_seconds())

            # Presigned URL용 쿼리 파라미터
            request_parameters = {
                'X-Amz-Algorithm': self.hashing_algorithm,
                'X-Amz-Credential': f"{self.access_key}/{date_stamp}/{self.region}/{self.service_name}/{self.request_type}",
                'X-Amz-Date': time_stamp,
                'X-Amz-Expires': str(expires_in_seconds),
                'X-Amz-SignedHeaders': 'host'
            }

            headers = {'host': self.host}

            credential_scope = self._create_credential_scope(date_stamp)
            canonical_request = self._create_canonical_request(http_method, request_path, request_parameters, headers)
            string_to_sign = self._create_string_to_sign(time_stamp, credential_scope, canonical_request)
            signature_key = self._create_signature_key(date_stamp)

            import hmac
            import hashlib
            signature = hmac.new(signature_key, string_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()

            # URL 생성
            query_string = self._create_standardized_query_parameters(request_parameters)
            url = f"{self.endpoint}{request_path}?{query_string}&X-Amz-Signature={signature}"

            return url
        except Exception as e:
            logger.error(f"파일 '{object_name}'의 URL 생성 중 예외: {str(e)}")
            logger.error(f"상세 에러: {traceback.format_exc()}")
            return None

    async def save_object(
            self,
            bucket_name: str,
            object_name: str,
            data: BinaryIO,
            content_type: str,
            encoding: str
    ) -> Optional[str]:
        """객체를 저장하고 ETag를 반환"""
        try:
            # 버킷이 없으면 생성
            self.create_bucket_if_not_exists(bucket_name)

            # 파일 포인터를 처음으로 이동
            data.seek(0)
            content = data.read()

            http_method = 'PUT'
            request_path = f'/{bucket_name}/{object_name}'

            time = datetime.now()
            time_stamp = time.strftime(self.time_format)

            headers = {
                'x-amz-date': time_stamp,
                'x-amz-content-sha256': self.payload_hash,
                'x-amz-acl': 'public-read',
                'content-type': content_type,
                'host': self.host
            }

            self._sign_request(http_method, request_path, headers, time)

            # URL 인코딩된 request_path 생성
            encoded_request_path = self._encode_path(request_path)
            request_url = self.endpoint + encoded_request_path

            r = requests.put(request_url, headers=headers, data=content)

            if r.status_code == 200:
                etag = r.headers.get('ETag', '').strip('"')
                logger.info(f"객체 '{object_name}'이 성공적으로 저장되었습니다. ETag: {etag}")
                return etag
            else:
                logger.error(f"객체 '{object_name}' 저장 실패: {r.status_code} - {r.text}")
                return None
        except Exception as e:
            logger.error(f"객체 '{object_name}' 저장 중 예외: {str(e)}")
            return None

    def delete_file(self, bucket_name: str, object_name: str) -> bool:
        """NCloud Object Storage에서 파일 삭제"""
        try:
            http_method = 'DELETE'
            request_path = f'/{bucket_name}/{object_name}'

            time = datetime.now()
            time_stamp = time.strftime(self.time_format)

            headers = {
                'x-amz-date': time_stamp,
                'x-amz-content-sha256': self.payload_hash,
                'host': self.host
            }

            self._sign_request(http_method, request_path, headers, time)

            # URL 인코딩된 request_path 생성
            encoded_request_path = self._encode_path(request_path)
            request_url = self.endpoint + encoded_request_path

            r = requests.delete(request_url, headers=headers)

            if r.status_code in [200, 204]:
                logger.info(f"파일 '{object_name}'이 버킷 '{bucket_name}'에서 성공적으로 삭제되었습니다.")
                return True
            else:
                logger.error(f"파일 '{object_name}' 삭제 실패: {r.status_code} - {r.text}")
                return False
        except Exception as e:
            logger.error(f"파일 '{object_name}' 삭제 중 예외: {str(e)}")
            return False
