from app.common.infra.event.decorators import event_handler, event_register_handlers
from app.core.database import transactional
from app.core.error_codes import ErrorCode
from app.core.exception import APIException
from app.target.application.command.target_command import GetTargetInfoCommand
from app.target.application.query.target_query import TargetQuery
from app.target.domain.repository.target_repository import TargetRepository

@event_register_handlers()
class TargetApplicationService:
    
    def __init__(self,
                 target_repository: TargetRepository
                ):
        self.target_repository = target_repository
    
    @transactional
    async def get_all_targets(self, target_ids: list[int] | None = None) -> list[TargetQuery]:
        if target_ids:
            self.target_repository.find_by_ids(target_ids=target_ids)
        else:
            targets = self.target_repository.find_all_active()
        return TargetQuery.from_entity(targets)
    
    @event_handler("GET_TARGET_INFO_REQUESTED")
    @transactional
    async def get_target_by_command(
        self,
        command: GetTargetInfoCommand
    ) -> TargetQuery:
        if command.target_id:
            target = self.target_repository.find_by_id(command.target_id)
        elif command.target_code:
            target = self.target_repository.find_by_code(command.target_code)
        else:
            APIException(ErrorCode.INVALID_REQUEST)
        return TargetQuery.from_entity(target)