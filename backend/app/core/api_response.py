from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Any, Optional, Generic, TypeVar

T = TypeVar("T")

class ErrorDetail(BaseModel):
    code: str
    message: str

class ApiResponseSchema(BaseModel, Generic[T]):
    status: int
    message: str
    data: T|dict
    error: ErrorDetail|dict


# 표준 API 응답 클래스
class ApiResponse(JSONResponse):
    def __init__(
        self, 
        data: Any = None, 
        message: str = "ok", 
        status_code: int = 200, 

        error_code: Optional[str] = None,
        error_message: Optional[str] = None,
        *args, 
        **kwargs
    ) -> None:
        # 에러 정보가 제공된 경우 에러 응답 생성
        if error_code and error_message:
            message = "failed"
            error = ErrorDetail(code=error_code, message=error_message)
            data = {}
        else:
            error = {}
            
        content = ApiResponseSchema(
            status=status_code,
            message=message,
            data=data,
            error=error
        ).model_dump(by_alias=True, mode='json')
        
        super().__init__(content=content, status_code=status_code, *args, **kwargs)