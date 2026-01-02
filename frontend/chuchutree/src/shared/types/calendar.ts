// 캘린더 관련 타입 정의

import { TierKey } from "@/shared/constants/tierSystem";

export interface TagAlias {
  alias: string;
}

export interface TagTarget {
  targetId: number;
  targetCode: string;
  targetDisplayName: string;
}

export interface Tag {
  tagId: number;
  tagCode: string;
  tagDisplayName: string;
  tagTarget: TagTarget[];
  tagAliases: TagAlias[];
}

export interface RecommendReason {
  reason: string;
  additionalData: Record<string, any> | null;
}

export interface Problem {
  problemId: number;
  problemTitle: string;
  problemTierLevel: number;
  problemTierName: TierKey;
  problemClassLevel: number;
  recommandReasons: RecommendReason[];
  tags: Tag[];
}

export interface MonthlyData {
  date: string; // YYYY-MM-DD 형식
  solvedProblemCount: number;
  willSolveProblemCount: number;
  solvedProblems: Problem[];
  willSolveProblem: Problem[]; // API 응답의 오타를 그대로 유지
}

export interface CalendarApiResponse {
  status: number;
  message: string;
  data: {
    totalProblemCount: number;
    monthlyData: MonthlyData[];
  };
  error: Record<string, any>;
}

// react-big-calendar에서 사용할 이벤트 타입
export interface CalendarEvent {
  title: string;
  start: Date;
  end: Date;
  resource: {
    type: 'solved' | 'willSolve';
    problem: Problem;
    tagCode: string;
  };
}
