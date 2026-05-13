"""ProblemTag Mapper"""
from app.common.domain.vo.identifiers import ProblemId, TagId
from app.problem.domain.entity.problem_tag import ProblemTag
from app.problem.infra.model.problem_tag import ProblemTagModel


class ProblemTagMapper:
    """ProblemTag Entity <-> Model 변환"""

    @staticmethod
    def to_entity(model: ProblemTagModel) -> ProblemTag:
        """Model -> Entity"""
        return ProblemTag(
            problem_tag_id=model.problem_tag_id,
            problem_id=ProblemId(model.problem_id),
            tag_id=TagId(model.tag_id),
            created_at=model.created_at
        )

    @staticmethod
    def to_model(entity: ProblemTag) -> ProblemTagModel:
        """Entity -> Model"""
        return ProblemTagModel(
            problem_tag_id=entity.problem_tag_id,
            problem_id=entity.problem_id.value,
            tag_id=entity.tag_id.value,
            created_at=entity.created_at
        )
