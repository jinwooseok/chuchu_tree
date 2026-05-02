import time
import logging
import asyncio
from functools import wraps
from typing import Callable, Any, Optional

logger = logging.getLogger(__name__)


def measure_time(
    log_level: int = logging.INFO,
    include_args: bool = False,
    include_result: bool = False,
    threshold_ms: Optional[float] = None
):
    """
    함수 실행시간을 측정하는 데코레이터

    Args:
        log_level: 로그 레벨 (기본: INFO)
        include_args: 함수 인자를 로그에 포함할지 여부
        include_result: 함수 결과를 로그에 포함할지 여부
        threshold_ms: 이 시간(ms) 이상일 때만 로그 출력 (None이면 항상 출력)

    Usage:
        @measure_time()
        def some_function():
            pass

        @measure_time(threshold_ms=1000, include_args=True)
        async def slow_function(arg1, arg2):
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            start_time = time.perf_counter()
            success = False
            result = None
            try:
                result = await func(*args, **kwargs)
                success = True
            except Exception as e:
                result = None
                success = False
                raise
            finally:
                end_time = time.perf_counter()
                execution_time_ms = (end_time - start_time) * 1000
    
                # 임계값 체크
                if threshold_ms is None or execution_time_ms >= threshold_ms:
                    _log_execution_time(
                        func.__name__,
                        execution_time_ms,
                        success,
                        args if include_args else None,
                        kwargs if include_args else None,
                        result if include_result else None,
                        log_level
                    )

            return result

        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            start_time = time.perf_counter()
            success = False
            result = None
            try:
                result = func(*args, **kwargs)
                success = True
            except Exception as e:
                result = None
                success = False
                raise
            finally:
                end_time = time.perf_counter()
                execution_time_ms = (end_time - start_time) * 1000

                # 임계값 체크
                if threshold_ms is None or execution_time_ms >= threshold_ms:
                    _log_execution_time(
                        func.__name__,
                        execution_time_ms,
                        success,
                        args if include_args else None,
                        kwargs if include_args else None,
                        result if include_result else None,
                        log_level
                    )

            return result

        # async 함수인지 확인
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def _log_execution_time(
    func_name: str,
    execution_time_ms: float,
    success: bool,
    args: Optional[tuple] = None,
    kwargs: Optional[dict] = None,
    result: Any = None,
    log_level: int = logging.INFO
):
    """실행시간 로그 출력"""

    # 기본 메시지
    status = "✅ SUCCESS" if success else "❌ FAILED"
    base_msg = f"⏱️  {func_name} - {execution_time_ms:.2f}ms ({status})"

    # 추가 정보
    details = []

    if args:
        # 너무 긴 인자는 축약
        args_str = str(args)
        if len(args_str) > 100:
            args_str = args_str[:97] + "..."
        details.append(f"args={args_str}")

    if kwargs:
        kwargs_str = str(kwargs)
        if len(kwargs_str) > 100:
            kwargs_str = kwargs_str[:97] + "..."
        details.append(f"kwargs={kwargs_str}")

    if result is not None:
        result_str = str(result)
        if len(result_str) > 100:
            result_str = result_str[:97] + "..."
        details.append(f"result={result_str}")

    # 최종 로그 메시지
    if details:
        final_msg = f"{base_msg} | {' | '.join(details)}"
    else:
        final_msg = base_msg

    logger.log(log_level, final_msg)


class PerformanceTimer:
    """성능 측정을 위한 컨텍스트 매니저"""

    def __init__(self, name: str, log_level: int = logging.INFO):
        self.name = name
        self.log_level = log_level
        self.start_time = None

    def __enter__(self):
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time is not None:
            end_time = time.perf_counter()
            execution_time_ms = (end_time - self.start_time) * 1000

            success = exc_type is None
            status = "✅ SUCCESS" if success else "❌ FAILED"
            message = f"⏱️  {self.name} - {execution_time_ms:.2f}ms ({status})"

            logger.log(self.log_level, message)


# 편의 함수들
def measure_fast(func):
    """빠른 측정 - 기본 설정으로 데코레이터 적용"""
    return measure_time()(func)


def measure_slow(threshold_ms: float = 1000):
    """느린 함수 측정 - 임계값 이상일 때만 로그"""
    return measure_time(threshold_ms=threshold_ms, include_args=True)


def measure_detailed(func):
    """상세 측정 - 인자와 결과 포함"""
    return measure_time(include_args=True, include_result=True)(func)