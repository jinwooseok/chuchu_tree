# Domain Models

# User Domain
from app.user.infra.model.user_account import UserAccountModel
from app.user.infra.model.account_link import AccountLinkModel
from app.user.infra.model.user_target import UserTargetModel

# Tier Domain
from app.tier.infra.model.tier import TierModel

# Baekjoon Domain
from app.baekjoon.infra.model.bj_account import BjAccountModel
from app.baekjoon.infra.model.tier_history import TierHistoryModel
from app.baekjoon.infra.model.tag_skill_history import TagSkillHistoryModel

# Activity Domain
from app.activity.infra.model.problem_date_record import ProblemDateRecordModel
from app.activity.infra.model.user_problem_status import UserProblemStatusModel
from app.activity.infra.model.tag_custom import TagCustomModel
from app.activity.infra.model.user_date_record import UserDateRecordModel

# Tag Domain
from app.tag.infra.model.tag import TagModel
from app.tag.infra.model.tag_relation import TagRelationModel

# Target Domain
from app.target.infra.model.target import TargetModel
from app.target.infra.model.target_tag import TargetTagModel

# Problem Domain
from app.problem.infra.model.problem import ProblemModel
from app.baekjoon.infra.model.problem_history import ProblemHistoryModel
from app.problem.infra.model.problem_tag import ProblemTagModel

# Recommendation Domain
from app.recommendation.infra.model.problem_recommendation_level_filter import ProblemRecommendationLevelFilterModel
from app.recommendation.infra.model.tag_skill import TagSkillModel

# Common Domain
from app.common.infra.model.system_log import SystemLogModel

__all__ = [
    # User
    "UserAccountModel",
    "AccountLinkModel",
    "UserTargetModel",
    # Tier
    "TierModel",
    # Baekjoon
    "BjAccountModel",
    "TierHistoryModel",
    "TagSkillHistoryModel",
    # Activity
    "TagCustomModel",
    "UserProblemStatusModel",
    "ProblemDateRecordModel",
    "UserDateRecordModel",
    # Tag
    "TagModel",
    "TagRelationModel",
    # Target
    "TargetModel",
    "TargetTagModel",
    # Problem
    "ProblemModel",
    "ProblemHistoryModel",
    "ProblemTagModel",
    # Recommendation
    "ProblemRecommendationLevelFilterModel",
    "TagSkillModel",
    # Common
    "SystemLogModel",
]
