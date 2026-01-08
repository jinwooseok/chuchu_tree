from app.common.infra.event.decorators import event_handler, event_register_handlers
from app.core.database import transactional
from app.core.error_codes import ErrorCode
from app.core.exception import APIException
from app.tag.application.command.tag_command import GetTagInfoCommand
from app.tag.application.query.tag_query import TagSummaryQuery
from app.tag.domain.repository.tag_repository import TagRepository


@event_register_handlers()
class TagApplicationService:
    
    def __init__(self,
                 tag_repository: TagRepository
                ):
        self.tag_repository = tag_repository
    
    @transactional
    async def get_tags(self, 
                       tag_ids: list[int] | None = None, 
                       system_excluded_yn: bool = True,
                       user_excluded_yn: bool = True,
                        ) -> list[TagSummaryQuery]:
        if tag_ids:
            self.tag_repository.find_by_ids(tag_ids=tag_ids)
        else:
            tags = self.tag_repository.find_active_tags()
        return [TagSummaryQuery.from_entity(tag) for tag in tags]
    
    @event_handler("GET_TAG_INFO_REQUESTED")
    @transactional
    async def get_tag_by_command(
        self,
        command: GetTagInfoCommand
    ) -> TagSummaryQuery:
        if command.tag_id:
            tag = self.tag_repository.find_by_id(command.tag_id)
        elif command.tag_code:
            tag = self.tag_repository.find_by_code(command.tag_code)
        else:
            APIException(ErrorCode.INVALID_REQUEST)
        return TagSummaryQuery.from_entity(tag)