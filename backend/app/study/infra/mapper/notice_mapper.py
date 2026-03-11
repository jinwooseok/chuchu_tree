from app.common.domain.enums import NoticeCategoryDetail
from app.common.domain.vo.identifiers import NoticeId, UserAccountId
from app.study.domain.entity.notice import Notice
from app.study.infra.model.notice import NoticeModel

class NoticeMapper:
    @staticmethod
    def to_model(entity: Notice) -> NoticeModel:
        model = NoticeModel()
        if entity.notice_id is not None:
            model.notice_id = entity.notice_id.value
        model.recipient_user_account_id = entity.recipient_user_account_id.value
        model.category = entity.category
        model.category_detail = entity.category_detail.value if entity.category_detail else None
        model.content = entity.content
        model.is_read = entity.is_read
        model.created_at = entity.created_at
        model.updated_at = entity.updated_at
        model.deleted_at = entity.deleted_at
        return model

    @staticmethod
    def to_entity(model: NoticeModel) -> Notice:
        category_detail = None
        if model.category_detail:
            try:
                category_detail = NoticeCategoryDetail(model.category_detail)
            except ValueError:
                category_detail = None

        return Notice(
            notice_id=NoticeId(model.notice_id),
            recipient_user_account_id=UserAccountId(model.recipient_user_account_id),
            category=model.category,
            category_detail=category_detail,
            content=model.content,
            is_read=model.is_read,
            created_at=model.created_at,
            updated_at=model.updated_at,
            deleted_at=model.deleted_at,
        )
