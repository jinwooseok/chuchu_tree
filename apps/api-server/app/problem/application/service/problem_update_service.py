"""ProblemUpdateService - 신규 문제 점진적 업데이트 서비스"""

import logging
from datetime import datetime

import httpx

from app.problem.infra.model.problem import ProblemModel
from app.problem.infra.model.problem_tag import ProblemTagModel
from app.tag.infra.repository.tag_repository_impl import TagRepositoryImpl
from app.core.database import Database
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

SOLVEDAC_PROBLEM_SHOW_URL = "https://solved.ac/api/v3/problem/show"


class ProblemUpdateService:
    """
    신규 문제 점진적 업데이트 서비스

    solved.ac에 존재하지만 DB에 없는 문제를 발견하면
    자동으로 DB에 추가하는 역할을 담당합니다.
    """

    def __init__(self, db: Database):
        self.db = db

    @property
    def session(self) -> AsyncSession:
        return self.db.get_current_session()

    async def ensure_problem_exists(self, problem_id: int) -> bool:
        """
        문제가 DB에 없으면 solved.ac API에서 가져와 INSERT합니다.

        Args:
            problem_id: 문제 ID

        Returns:
            True: 문제가 DB에 있거나 INSERT 성공
            False: solved.ac에서도 찾을 수 없음 (skip 대상)
        """
        # 1. DB에서 problem_id 확인
        stmt = select(ProblemModel).where(ProblemModel.problem_id == problem_id)
        result = await self.session.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing:
            return True

        # 2. solved.ac API 호출
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    SOLVEDAC_PROBLEM_SHOW_URL,
                    params={"problemId": problem_id}
                )
                if response.status_code == 404:
                    logger.warning(f"[ProblemUpdateService] 문제를 solved.ac에서 찾을 수 없음: {problem_id}")
                    return False
                if response.status_code != 200:
                    logger.error(f"[ProblemUpdateService] solved.ac API 오류: status={response.status_code}, problem_id={problem_id}")
                    return False

                data = response.json()
        except Exception as e:
            logger.error(f"[ProblemUpdateService] solved.ac API 호출 실패: {e}, problem_id={problem_id}")
            return False

        # 3. 문제 INSERT
        try:
            level = data.get("level", 0)
            title = data.get("titleKo", "") or data.get("title", "")
            solved_user_count = data.get("acceptedUserCount", 0)
            now = datetime.now()

            problem_model = ProblemModel(
                problem_id=problem_id,
                problem_title=title,
                problem_tier_level=level if level > 0 else 1,
                solved_user_count=solved_user_count,
                created_at=now,
                updated_at=now
            )
            self.session.add(problem_model)
            await self.session.flush()

            # 4. 태그 INSERT
            tags = data.get("tags", [])
            for tag_data in tags:
                tag_name = tag_data.get("key", "")
                if not tag_name:
                    continue

                # tag 테이블에서 tag_code로 tag_id 조회
                tag_stmt = select(
                    __import__('app.tag.infra.model.tag', fromlist=['TagModel']).TagModel
                ).where(
                    __import__('app.tag.infra.model.tag', fromlist=['TagModel']).TagModel.tag_code == tag_name
                )
                tag_result = await self.session.execute(tag_stmt)
                tag_model = tag_result.scalar_one_or_none()

                if tag_model:
                    problem_tag = ProblemTagModel(
                        problem_id=problem_id,
                        tag_id=tag_model.tag_id,
                        created_at=now
                    )
                    self.session.add(problem_tag)

            await self.session.flush()
            logger.info(f"[ProblemUpdateService] 문제 INSERT 완료: problem_id={problem_id}, title={title}")
            return True

        except Exception as e:
            logger.error(f"[ProblemUpdateService] 문제 INSERT 실패: {e}, problem_id={problem_id}")
            return False

    async def ensure_problems_exist(self, problem_ids: list[int]) -> list[int]:
        """
        여러 문제들을 확인하고 DB에 없는 것들을 INSERT합니다.

        Returns:
            실제로 존재하는 문제 ID 목록 (DB에 없고 solved.ac에서도 못 찾은 건 제외)
        """
        valid_ids = []
        for pid in problem_ids:
            if await self.ensure_problem_exists(pid):
                valid_ids.append(pid)
        return valid_ids
