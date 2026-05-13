from app.common.domain.vo.identifiers import StudyId, UserAccountId
from app.core.database import transactional
from app.core.error_codes import ErrorCode
from app.core.exception import APIException
from app.study.domain.repository.study_repository import StudyRepository


class ValidateStudyMemberUsecase:
    def __init__(self, study_repository: StudyRepository):
        self.study_repository = study_repository

    @transactional(readonly=True)
    async def execute(self, study_id: int, user_account_id: int) -> None:
        study = await self.study_repository.find_by_id(StudyId(study_id))
        if study is None:
            raise APIException(ErrorCode.STUDY_NOT_FOUND)
        if not study.is_member(UserAccountId(user_account_id)):
            raise APIException(ErrorCode.STUDY_NOT_MEMBER)
