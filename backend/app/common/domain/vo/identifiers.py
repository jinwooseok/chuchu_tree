from dataclasses import dataclass

@dataclass(frozen=True)
class UserAccountId:
    value: int

@dataclass(frozen=True)
class BaekjoonAccountId:
    value: str

@dataclass(frozen=True)
class TargetId:
    value: int

@dataclass(frozen=True)
class ProblemId:
    value: int

@dataclass(frozen=True)
class TagId:
    value: int
    
@dataclass(frozen=True)
class TagSkillId:
    value: int
    
@dataclass(frozen=True)
class TierId:
    value: int
    
@dataclass(frozen=True)
class UserActivityId:
    value: int

@dataclass(frozen=True)
class LevelFilterId:
    """Value Object - 필터 ID"""
    value: int