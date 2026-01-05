"""Problem Mapper"""
from app.common.domain.vo.identifiers import ProblemId, TagId
from app.common.domain.vo.primitives import TierLevel
from app.problem.domain.entity.problem import Problem
from app.problem.domain.entity.problem_tag import ProblemTag
from app.problem.infra.model.problem import ProblemModel


class ProblemMapper:
    """Problem Entity <-> Model 변환"""

    @staticmethod
    def to_entity(model: ProblemModel, tags: list[ProblemTag] = None) -> Problem:
        """Model -> Entity"""
        return Problem(
            problem_id=ProblemId(model.problem_id),
            title=model.problem_title,
            tier_level=TierLevel(model.problem_tier_level),
            class_level=model.class_level,
            created_at=model.created_at,
            updated_at=model.updated_at,
            deleted_at=model.deleted_at,
            tags=tags or [],
            update_histories=[]
        )

    @staticmethod
    def to_model(entity: Problem) -> ProblemModel:
        """Entity -> Model"""
        return ProblemModel(
            problem_id=entity.problem_id.value,
            problem_title=entity.title,
            problem_tier_level=entity.tier_level.value,
            class_level=entity.class_level,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            deleted_at=entity.deleted_at
        )
