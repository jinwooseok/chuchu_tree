from app.common.domain.vo.identifiers import StudyId, StudyInvitationId, UserAccountId
from app.study.domain.entity.study_invitation import StudyInvitation
from app.study.infra.model.study_invitation import StudyInvitationModel


class StudyInvitationMapper:
    @staticmethod
    def to_model(entity: StudyInvitation) -> StudyInvitationModel:
        model = StudyInvitationModel()
        if entity.invitation_id is not None:
            model.invitation_id = entity.invitation_id.value
        model.study_id = entity.study_id.value
        model.invitee_user_account_id = entity.invitee_user_account_id.value
        model.inviter_user_account_id = entity.inviter_user_account_id.value
        model.status = entity.status
        model.responded_at = entity.responded_at
        model.created_at = entity.created_at
        model.updated_at = entity.updated_at
        model.deleted_at = entity.deleted_at
        return model

    @staticmethod
    def to_entity(model: StudyInvitationModel) -> StudyInvitation:
        return StudyInvitation(
            invitation_id=StudyInvitationId(model.invitation_id),
            study_id=StudyId(model.study_id),
            invitee_user_account_id=UserAccountId(model.invitee_user_account_id),
            inviter_user_account_id=UserAccountId(model.inviter_user_account_id),
            status=model.status,
            responded_at=model.responded_at,
            created_at=model.created_at,
            updated_at=model.updated_at,
            deleted_at=model.deleted_at,
        )
