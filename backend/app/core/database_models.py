# Domain Models

# User Domain
from app.user.infra.model.user_account import UserAccount
from app.user.infra.model.account_link import AccountLink
from app.user.infra.model.user_target import UserTarget

# Tier Domain
from app.tier.infra.model.tier import Tier

# Baekjoon Domain
from app.baekjoon.infra.model.bj_account import BjAccount
from app.baekjoon.infra.model.tier_history import TierHistory
from app.baekjoon.infra.model.tag_skill_history import TagSkillHistory

# Activity Domain
from app.activity.infra.model.problem_record import ProblemRecord
from app.activity.infra.model.problem_banned_record import ProblemBannedRecord
from app.activity.infra.model.will_solve_problem import WillSolveProblem
from app.activity.infra.model.tag_custom import TagCustom

# Tag Domain
from app.tag.infra.model.tag import Tag
from app.tag.infra.model.tag_relation import TagRelation

# Target Domain
from app.target.infra.model.target import Target
from app.target.infra.model.target_tag import TargetTag

# Problem Domain
from app.problem.infra.model.problem import Problem
from app.problem.infra.model.problem_history import ProblemHistory
from app.problem.infra.model.problem_update_history import ProblemUpdateHistory
from app.problem.infra.model.problem_tag import ProblemTag

# Recommendation Domain
from app.recommendation.infra.model.problem_recommendation_level_filter import ProblemRecommendationLevelFilter
from app.recommendation.infra.model.tag_skill import TagSkill

__all__ = [
    # User
    "UserAccount",
    "AccountLink",
    "UserTarget",
    # Tier
    "Tier",
    # Baekjoon
    "BjAccount",
    "TierHistory",
    "TagSkillHistory",
    # Activity
    "ProblemRecord",
    "ProblemBannedRecord",
    "WillSolveProblem",
    "TagCustom",
    # Tag
    "Tag",
    "TagRelation",
    # Target
    "Target",
    "TargetTag",
    # Problem
    "Problem",
    "ProblemHistory",
    "ProblemUpdateHistory",
    "ProblemTag",
    # Recommendation
    "ProblemRecommendationLevelFilter",
    "TagSkill",
]
