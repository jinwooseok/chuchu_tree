from app.common.infra.event.decorators import event_handler, event_register_handlers
from app.core.database import transactional
from app.core.error_codes import ErrorCode
from app.core.exception import APIException
from app.tag.application.command.tag_command import GetTagInfoCommand, GetTagInfosCommand
from app.tag.application.query.tag_query import TagInfosQuery, TagSummaryQuery
from app.tag.domain.repository.tag_repository import TagRepository


@event_register_handlers()
class TagApplicationService:
    
    def __init__(self,
                 tag_repository: TagRepository
                ):
        self.tag_repository = tag_repository
    
    @event_handler("GET_TAG_INFOS_REQUESTED")
    @transactional
    async def get_tags(self, command: GetTagInfosCommand) -> TagInfosQuery:
        tags = await self.tag_repository.find_by_ids(tag_ids=command.tag_ids)
        tag_queries = [TagSummaryQuery.from_entity(tag) for tag in tags]
        return TagInfosQuery(tags=tag_queries)
    
    @event_handler("GET_TAG_INFO_REQUESTED")
    @transactional
    async def get_tag_by_command(
        self,
        command: GetTagInfoCommand
    ) -> TagSummaryQuery:
        if command.tag_id:
            tag = await self.tag_repository.find_by_id(command.tag_id)
        elif command.tag_code:
            tag = await self.tag_repository.find_by_code(command.tag_code)
        else:
            APIException(ErrorCode.INVALID_REQUEST)

        # 2. 태그 정보가 없으면 예외 처리
        if not tag:
            raise APIException(ErrorCode.TAG_NOT_FOUND, f"Tag with code {command.tag_code} not found.")

        return TagSummaryQuery.from_entity(tag)