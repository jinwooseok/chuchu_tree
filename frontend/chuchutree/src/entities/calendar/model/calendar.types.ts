import { TagKey } from '@/shared/constants/tagSystem';
import { TIER_INFO, TierKey } from '@/shared/constants/tierSystem';

export interface TagTargets {
  targetId: number;
  targetCode: string;
  targetDisplayName: string;
}

export interface TagAliases {
  alias: string;
}

export interface Tags {
  tagId: number;
  tagCode: TagKey;
  tagDisplayName: string;
  tagTargets: TagTargets[];
  tagAliases: TagAliases[];
}

export interface RecommendReason {
  reason: string;
  additionalData: Record<string, any> | null;
}

export interface SolvedProblems {
  problemId: number;
  realSolvedYn: boolean;
  problemTitle: string;
  problemTierLevel: keyof typeof TIER_INFO;
  problemTierName: TierKey;
  problemClassLevel: number;
  tags: Tags[];
}

export interface WillSolveProblems {
  problemId: number;
  problemTitle: string;
  problemTierLevel: keyof typeof TIER_INFO;
  problemTierName: TierKey;
  problemClassLevel: number;
  tags: Tags[];
}

// Problem: SolvedProblems와 WillSolveProblems의 공통 타입
export type Problem = SolvedProblems | WillSolveProblems;

export interface MonthlyData {
  targetDate: string;
  solvedProblemCount: number;
  willSolveProblemCount: number;
  solvedProblems: SolvedProblems[];
  willSolveProblems: WillSolveProblems[];
}

export interface Calendar {
  totalProblemCount: number;
  monthlyData: MonthlyData[];
}

// react-big-calendar에서 사용할 이벤트 타입
export interface CalendarEvent {
  title: string;
  start: Date;
  end: Date;
  resource: {
    type: 'solved' | 'willSolve';
    problem: SolvedProblems | WillSolveProblems;
    tagCode: string;
  };
}

// 풀문제 업데이트, 푼문제 업데이트 request data
export interface UpdateProblemsData {
  date: string;
  problemIds: number[];
}

// 문제 검색
export interface SearchProblems {
  problems: {
    idBaseTotalCount: number;
    titleBaseTotalCount: number;
    idBase: WillSolveProblems[];
    titleBase: WillSolveProblems[];
  };
}
