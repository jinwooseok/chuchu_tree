from dataclasses import dataclass, field
from datetime import datetime, date

from app.baekjoon.domain.entity.problem_history import ProblemHistory
from app.baekjoon.domain.entity.streak import Streak
from app.baekjoon.domain.entity.tag_skill_history import TagSkillHistory
from app.baekjoon.domain.entity.tier_history import TierHistory
from app.common.domain.vo.primitives import Rating
from app.common.domain.vo.primitives import Statistics
from app.common.domain.vo.identifiers import BaekjoonAccountId, ProblemId, TagId, TagSkillId, TierId

@dataclass
class BaekjoonAccount:
    """Aggregate Root - 백준 계정"""
    bj_account_id: BaekjoonAccountId
    tier_start_date: str|None
    current_tier_id: TierId
    rating: Rating
    statistics: Statistics
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime|None = None
    tier_histories: list[TierHistory] = field(default_factory=list)
    tag_skill_histories: list[TagSkillHistory] = field(default_factory=list)
    problem_histories: list[ProblemHistory] = field(default_factory=list)
    streaks: list[Streak] = field(default_factory=list)
    
    @staticmethod
    def create(
        bj_account_id: BaekjoonAccountId,
        tier_id: TierId,
    ) -> 'BaekjoonAccount':
        now = datetime.now()
        return BaekjoonAccount(
            bj_account_id=bj_account_id,
            tier_start_date=date.today(),
            current_tier_id=tier_id,
            rating=Rating(0),
            statistics=Statistics(0, 0, 0),
            created_at=now,
            updated_at=now,
            deleted_at=None,
            tier_histories=[],
            tag_skill_histories=[],
            problem_histories=[],
            streaks=[]
        )
    
    def update_tier(self, new_tier_id: TierId) -> None:
        """도메인 로직 - 티어 업데이트"""
        if self.current_tier_id.value == new_tier_id.value:
            return
        
        self.tier_histories.append(
            TierHistory.create(
                self.bj_account_id,
                self.current_tier_id,
                new_tier_id
            )
        )
        self.current_tier_id = new_tier_id
        self.tier_start_date = date.today()
        self.updated_at = datetime.now()
    
    def update_statistics(
        self,
        contribution_count: int,
        class_level: int,
        longest_streak: int
    ) -> None:
        """도메인 로직 - 통계 업데이트"""
        self.statistics = Statistics(contribution_count, class_level, longest_streak)
        self.updated_at = datetime.now()
    
    def update_rating(self, new_rating: int) -> None:
        """도메인 로직 - 레이팅 업데이트"""
        self.rating = Rating(new_rating)
        self.updated_at = datetime.now()
    
    def record_problem_solved(self, problem_id: ProblemId, solved_date: date | None = None) -> None:
        """도메인 로직 - 문제 해결 기록 (시간 정보 없음)"""
        self.problem_histories.append(
            ProblemHistory.create(self.bj_account_id, problem_id, solved_date)
        )

    def add_streak(self, streak_date: date, solved_count: int) -> None:
        """도메인 로직 - 스트릭 추가"""
        self.streaks.append(
            Streak.create(self.bj_account_id, streak_date, solved_count)
        )
    
    def update_tag_skill(
        self,
        tag_id: TagId,
        new_skill_id: TagSkillId,
        prev_skill_id: TagSkillId|None = None
    ) -> None:
        """도메인 로직 - 태그 숙련도 변경"""
        self.tag_skill_histories.append(
            TagSkillHistory.create(
                self.bj_account_id,
                tag_id,
                new_skill_id,
                prev_skill_id
            )
        )
        
    def add_or_update_streak(self, streak_date: date, solved_count: int) -> None:
        """기존 스트릭이 있으면 업데이트, 없으면 추가"""
        existing = next((s for s in self.streaks if s.streak_date == streak_date), None)
        if existing:
            existing.update_solved_count(solved_count)
        else:
            self.streaks.append(Streak.create(self.bj_account_id, streak_date, solved_count))

    def record_problem_with_streak(self, problem_id: ProblemId, streak: 'Streak') -> None:
        """문제와 스트릭을 연결하여 기록"""
        history = ProblemHistory.create(self.bj_account_id, problem_id)
        
        # Heuristic: 전달받은 스트릭 객체를 참조
        # 나중에 Repository에서 save할 때, streak의 ID가 생성된 후 history의 streak_id로 들어감
        history.link_to_streak(streak) 
        self.problem_histories.append(history)