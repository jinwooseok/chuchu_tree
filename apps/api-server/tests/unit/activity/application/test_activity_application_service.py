import pytest
from datetime import date
from unittest.mock import AsyncMock, MagicMock

from app.activity.application.command.ban_problem_command import BanProblemCommand
from app.activity.application.command.tag_custom_command import TagCustomCommand
from app.activity.application.command.update_will_solve_problems import UpdateWillSolveProblemsCommand
from app.activity.application.command.update_solved_problems_command import UpdateSolvedProblemsCommand
from app.activity.application.command.batch_create_solved_problems_command import BatchCreateSolvedProblemsCommand
from app.activity.application.command.set_representative_tag_command import SetProblemRepresentativeTagCommand
from app.activity.application.service.activity_application_service import ActivityApplicationService
from app.activity.domain.entity.user_activity import UserActivity
from app.activity.domain.entity.user_problem_status import UserProblemStatus
from app.common.domain.vo.identifiers import ProblemId, TagId, UserAccountId
from app.core.exception import APIException


def _make_service() -> ActivityApplicationService:
    service = ActivityApplicationService(
        user_activity_repository=AsyncMock(),
        domain_event_bus=AsyncMock(),
        baekjoon_account_repository=AsyncMock(),
        problem_history_repository=AsyncMock(),
    )
    # Default mock returns
    service.baekjoon_account_repository.find_by_user_id.return_value = None
    service.user_activity_repository.find_problem_records_by_problem_ids.return_value = []
    service.user_activity_repository.find_will_solve_problems_by_date.return_value = []
    service.user_activity_repository.find_will_solve_problems_by_problem_ids.return_value = []
    service.user_activity_repository.find_problem_records_by_date.return_value = []
    return service


def _make_activity(user_id: int = 1) -> UserActivity:
    return UserActivity.create(UserAccountId(user_id))


class TestUpdateWillSolveProblems:
    """update_will_solve_problems() 테스트"""

    async def test_update_new_problems(self, mock_database_context):
        service = _make_service()

        command = UpdateWillSolveProblemsCommand(
            user_account_id=1,
            solved_date=date(2025, 1, 15),
            problem_ids=[1000, 2000, 3000]
        )

        await service.update_will_solve_problems(command)

        service.user_activity_repository.save_all_will_solve_problems.assert_called_once()

    async def test_update_with_duplicate_ids_raises(self, mock_database_context):
        service = _make_service()

        command = UpdateWillSolveProblemsCommand(
            user_account_id=1,
            solved_date=date(2025, 1, 15),
            problem_ids=[1000, 1000]
        )

        with pytest.raises(APIException) as exc_info:
            await service.update_will_solve_problems(command)

        assert exc_info.value.error_code == "DUPLICATED_ORDER"

    async def test_update_empty_list_deletes_existing(self, mock_database_context):
        service = _make_service()

        # Simulate existing problems on that date
        existing = UserProblemStatus.create_will_solve(
            user_account_id=UserAccountId(1),
            problem_id=ProblemId(1000),
            marked_date=date(2025, 1, 15)
        )
        service.user_activity_repository.find_will_solve_problems_by_date.return_value = [existing]

        command = UpdateWillSolveProblemsCommand(
            user_account_id=1,
            solved_date=date(2025, 1, 15),
            problem_ids=[]
        )

        await service.update_will_solve_problems(command)

        service.user_activity_repository.save_all_will_solve_problems.assert_called_once()
        saved = service.user_activity_repository.save_all_will_solve_problems.call_args[0][0]
        # 삭제 처리된 경우 활성 date_record가 없어야 함
        assert all(not p.is_will_solve() for p in saved)


class TestUpdateSolvedProblems:
    """update_solved_problems() 테스트"""

    async def test_update_new_solved_problems(self, mock_database_context):
        service = _make_service()

        command = UpdateSolvedProblemsCommand(
            user_account_id=1,
            solved_date=date(2025, 1, 15),
            problem_ids=[1000, 2000]
        )

        await service.update_solved_problems(command)

        service.user_activity_repository.save_all_problem_records.assert_called_once()

    async def test_solved_removes_will_solve(self, mock_database_context):
        service = _make_service()

        # Existing will_solve that should be deleted
        will_solve = UserProblemStatus.create_will_solve(
            user_account_id=UserAccountId(1),
            problem_id=ProblemId(1000),
            marked_date=date(2025, 1, 15)
        )
        service.user_activity_repository.find_will_solve_problems_by_problem_ids.return_value = [will_solve]

        command = UpdateSolvedProblemsCommand(
            user_account_id=1,
            solved_date=date(2025, 1, 15),
            problem_ids=[1000]
        )

        await service.update_solved_problems(command)

        # will_solve should have been saved with deleted_at set
        service.user_activity_repository.save_all_will_solve_problems.assert_called_once()


class TestBatchCreateSolvedProblems:
    """batch_create_solved_problems() 테스트"""

    async def test_batch_create_success(self, mock_database_context):
        service = _make_service()

        command = BatchCreateSolvedProblemsCommand(
            user_account_id=1,
            records=[
                (date(2025, 1, 15), [1000, 2000]),
                (date(2025, 1, 16), [3000]),
            ]
        )

        await service.batch_create_solved_problems(command)

        service.user_activity_repository.save_all_problem_records.assert_called()

    async def test_batch_with_duplicate_problem_ids_raises(self, mock_database_context):
        service = _make_service()

        command = BatchCreateSolvedProblemsCommand(
            user_account_id=1,
            records=[
                (date(2025, 1, 15), [1000]),
                (date(2025, 1, 16), [1000]),  # duplicate across dates
            ]
        )

        with pytest.raises(APIException) as exc_info:
            await service.batch_create_solved_problems(command)

        assert exc_info.value.error_code == "DUPLICATED_ORDER"

    async def test_batch_empty_records_returns_early(self, mock_database_context):
        service = _make_service()

        command = BatchCreateSolvedProblemsCommand(
            user_account_id=1,
            records=[]
        )

        await service.batch_create_solved_problems(command)

        service.user_activity_repository.save_all_problem_records.assert_not_called()


class TestBanProblem:
    """ban_problem() / unban_problem() 테스트"""

    async def test_ban_problem(self, mock_database_context):
        service = _make_service()
        activity = _make_activity()
        service.user_activity_repository.find_only_banned_problem_by_user_account_id.return_value = activity

        command = BanProblemCommand(
            user_account_id=1,
            problem_id=1000,
            problem_ban_yn=True
        )

        await service.ban_problem(command)

        service.user_activity_repository.save_problem_banned_record.assert_called_once()

    async def test_unban_problem(self, mock_database_context):
        service = _make_service()
        activity = _make_activity()
        activity.ban_problem(ProblemId(1000))
        service.user_activity_repository.find_only_banned_problem_by_user_account_id.return_value = activity

        command = BanProblemCommand(
            user_account_id=1,
            problem_id=1000,
            problem_ban_yn=False
        )

        await service.unban_problem(command)

        service.user_activity_repository.save_problem_banned_record.assert_called_once()


class TestBanTag:
    """ban_tag() / unban_tag() 테스트"""

    async def test_ban_tag(self, mock_database_context):
        service = _make_service()
        activity = _make_activity()
        service.user_activity_repository.find_only_tag_custom_by_user_account_id.return_value = activity

        tag_info = MagicMock()
        tag_info.tag_id = 1
        service.domain_event_bus.publish.return_value = tag_info

        command = TagCustomCommand(
            user_account_id=1,
            tag_code="dp",
            tag_ban_yn=True
        )

        await service.ban_tag(command)

        service.user_activity_repository.save_tag_custom.assert_called_once()

    async def test_unban_tag(self, mock_database_context):
        service = _make_service()
        activity = _make_activity()
        activity.customize_tag(TagId(1), exclude=True)
        service.user_activity_repository.find_only_tag_custom_by_user_account_id.return_value = activity

        tag_info = MagicMock()
        tag_info.tag_id = 1
        service.domain_event_bus.publish.return_value = tag_info

        command = TagCustomCommand(
            user_account_id=1,
            tag_code="dp",
            tag_ban_yn=False
        )

        await service.unban_tag(command)

        service.user_activity_repository.save_tag_custom.assert_called_once()

    async def test_unban_tag_not_found_raises(self, mock_database_context):
        service = _make_service()
        activity = _make_activity()
        service.user_activity_repository.find_only_tag_custom_by_user_account_id.return_value = activity

        service.domain_event_bus.publish.return_value = None

        command = TagCustomCommand(
            user_account_id=1,
            tag_code="nonexistent",
            tag_ban_yn=False
        )

        with pytest.raises(APIException) as exc_info:
            await service.unban_tag(command)

        assert exc_info.value.error_code == "TAG_NOT_FOUND"


class TestGetBannedProblems:
    """get_banned_problems() 테스트"""

    async def test_no_banned_problems(self, mock_database_context):
        service = _make_service()
        activity = _make_activity()
        service.user_activity_repository.find_only_banned_problem_by_user_account_id.return_value = activity

        result = await service.get_banned_problems(1)

        assert result.banned_problem_list == []

    async def test_with_banned_problems(self, mock_database_context):
        service = _make_service()
        activity = _make_activity()
        activity.ban_problem(ProblemId(1000))
        service.user_activity_repository.find_only_banned_problem_by_user_account_id.return_value = activity

        problems_info = MagicMock()
        problems_info.problems = {1000: MagicMock()}
        service.domain_event_bus.publish.return_value = problems_info

        result = await service.get_banned_problems(1)

        assert len(result.banned_problem_list) == 1


class TestGetBannedTags:
    """get_banned_tags() 테스트"""

    async def test_no_banned_tags(self, mock_database_context):
        service = _make_service()
        activity = _make_activity()
        service.user_activity_repository.find_only_tag_custom_by_user_account_id.return_value = activity

        result = await service.get_banned_tags(1)

        assert result.banned_tag_list == []
