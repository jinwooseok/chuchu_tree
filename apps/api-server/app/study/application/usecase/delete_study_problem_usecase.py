from app.common.domain.vo.identifiers import StudyId, StudyProblemId, UserAccountId
from app.core.database import transactional
from app.core.error_codes import ErrorCode
from app.core.exception import APIException
from app.study.application.command.study_command import DeleteStudyProblemCommand
from app.study.domain.repository.study_problem_repository import StudyProblemRepository
from app.study.domain.repository.study_repository import StudyRepository


class DeleteStudyProblemUsecase:
    def __init__(
        self,
        study_repository: StudyRepository,
        study_problem_repository: StudyProblemRepository,
    ):
        self.study_repository = study_repository
        self.study_problem_repository = study_problem_repository

    @transactional
    async def execute(self, command: DeleteStudyProblemCommand) -> None:
        study = await self.study_repository.find_by_id(StudyId(command.study_id))
        if study is None:
            raise APIException(ErrorCode.STUDY_NOT_FOUND)
        if not study.is_member(UserAccountId(command.requester_user_account_id)):
            raise APIException(ErrorCode.STUDY_NOT_MEMBER)

        problem = await self.study_problem_repository.find_by_id(StudyProblemId(command.study_problem_id))
        if problem is None:
            raise APIException(ErrorCode.STUDY_PROBLEM_NOT_FOUND)

        await self.study_problem_repository.soft_delete(problem)
