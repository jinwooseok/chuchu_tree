from app.common.domain.vo.identifiers import StudyId, StudyMemberId, UserAccountId
from app.study.domain.entity.study import Study
from app.study.domain.entity.study_member import StudyMember
from app.study.infra.model.study import StudyModel
from app.study.infra.model.study_member import StudyMemberModel


class StudyMemberMapper:
    @staticmethod
    def to_model(entity: StudyMember) -> StudyMemberModel:
        model = StudyMemberModel()
        if entity.study_member_id is not None:
            model.study_member_id = entity.study_member_id.value
        if entity.study_id is not None:
            model.study_id = entity.study_id.value
        model.user_account_id = entity.user_account_id.value
        model.role = entity.role
        model.joined_at = entity.joined_at
        model.created_at = entity.created_at
        model.updated_at = entity.updated_at
        model.deleted_at = entity.deleted_at
        return model

    @staticmethod
    def to_entity(model: StudyMemberModel) -> StudyMember:
        return StudyMember(
            study_member_id=StudyMemberId(model.study_member_id),
            study_id=StudyId(model.study_id),
            user_account_id=UserAccountId(model.user_account_id),
            role=model.role,
            joined_at=model.joined_at,
            created_at=model.created_at,
            updated_at=model.updated_at,
            deleted_at=model.deleted_at,
        )


class StudyMapper:
    @staticmethod
    def to_model(entity: Study) -> StudyModel:
        model = StudyModel()
        if entity.study_id is not None:
            model.study_id = entity.study_id.value
        model.study_name = entity.study_name
        model.owner_user_account_id = entity.owner_user_account_id.value
        model.description = entity.description
        model.max_members = entity.max_members
        model.created_at = entity.created_at
        model.updated_at = entity.updated_at
        model.deleted_at = entity.deleted_at
        model.members = [StudyMemberMapper.to_model(m) for m in entity.members]
        return model

    @staticmethod
    def to_entity(model: StudyModel) -> Study:
        return Study(
            study_id=StudyId(model.study_id),
            study_name=model.study_name,
            owner_user_account_id=UserAccountId(model.owner_user_account_id),
            description=model.description,
            max_members=model.max_members,
            created_at=model.created_at,
            updated_at=model.updated_at,
            deleted_at=model.deleted_at,
            members=[StudyMemberMapper.to_entity(m) for m in model.members],
        )
