from app.common.domain.vo.identifiers import StudyApplicationId, StudyId, UserAccountId
from app.study.domain.entity.study_application import StudyApplication
from app.study.infra.model.study_application import StudyApplicationModel


class StudyApplicationMapper:
    @staticmethod
    def to_model(entity: StudyApplication) -> StudyApplicationModel:
        model = StudyApplicationModel()
        if entity.application_id is not None:
            model.application_id = entity.application_id.value
        model.study_id = entity.study_id.value
        model.applicant_user_account_id = entity.applicant_user_account_id.value
        model.status = entity.status
        model.message = entity.message
        model.responded_at = entity.responded_at
        model.created_at = entity.created_at
        model.updated_at = entity.updated_at
        model.deleted_at = entity.deleted_at
        return model

    @staticmethod
    def to_entity(model: StudyApplicationModel) -> StudyApplication:
        return StudyApplication(
            application_id=StudyApplicationId(model.application_id),
            study_id=StudyId(model.study_id),
            applicant_user_account_id=UserAccountId(model.applicant_user_account_id),
            status=model.status,
            message=model.message,
            responded_at=model.responded_at,
            created_at=model.created_at,
            updated_at=model.updated_at,
            deleted_at=model.deleted_at,
        )
