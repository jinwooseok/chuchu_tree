import io
import logging
import os
import sys
import datetime
from datetime import date, datetime, timedelta


def setup_logging():
    # 기존 핸들러들 제거
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    handlers = [console_handler]
    
    # 환경에 따라 파일 로깅 제어 (로컬/테스트 환경에서는 파일 로깅 비활성화)
    env = os.getenv("environment", "local")
    if env == "prod":
        today = date.today()
        # 오늘 날짜 기준 주의 월요일 구하기
        monday = today - timedelta(days=today.weekday())  # weekday(): 월=0, 일=6
        sunday = monday + timedelta(days=6)

        LOG_FILE_PATH = f"logs/app_{monday.strftime('%y%m%d')}_{sunday.strftime('%y%m%d')}.log"
        
        os.makedirs(os.path.dirname(LOG_FILE_PATH), exist_ok=True)
        file_handler = logging.FileHandler(LOG_FILE_PATH, mode="a", encoding="utf-8")
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        handlers.append(file_handler)

    logging.basicConfig(
        level=logging.INFO,
        handlers=handlers,
        force=True
    )
    
    # uvicorn 로거들도 같은 설정 적용
    for name in ['uvicorn', 'uvicorn.error', 'uvicorn.access']:
        logger = logging.getLogger(name)
        # 기존 핸들러들 제거
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        # 새 핸들러들 추가
        for handler in handlers:
            logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.propagate = False