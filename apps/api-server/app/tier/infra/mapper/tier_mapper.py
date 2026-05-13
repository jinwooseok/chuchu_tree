"""Tier Entity <-> Model 매퍼"""

from app.common.domain.vo.identifiers import TierId
from app.tier.domain.entity.tier import Tier
from app.tier.infra.model.tier import TierModel


class TierMapper:
    """Tier Entity <-> Model 변환 매퍼"""

    @staticmethod
    def to_entity(model: TierModel) -> Tier:
        """Model -> Entity 변환"""
        return Tier(
            tier_id=TierId(model.tier_id),
            tier_level=model.tier_level,
            tier_code=model.tier_code,
            tier_rating=model.tier_rating,
            created_at=model.created_at,
            updated_at=model.updated_at,
            deleted_at=model.deleted_at
        )

    @staticmethod
    def to_model(entity: Tier) -> TierModel:
        """Entity -> Model 변환"""
        return TierModel(
            tier_id=entity.tier_id.value if entity.tier_id else None,
            tier_level=entity.tier_level,
            tier_code=entity.tier_code,
            tier_rating=entity.tier_rating,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            deleted_at=entity.deleted_at
        )
