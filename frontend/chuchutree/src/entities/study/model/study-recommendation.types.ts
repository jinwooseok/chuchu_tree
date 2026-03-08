import { Tags } from '@/entities/calendar';

export interface StudyRecommendMemberSolveInfo {
  userAccountId: number;
  bjAccountId: string;
  solved: boolean;
}

export interface StudyRecommendReason {
  reason: string;
  additionalData: string;
}

export interface StudyRecommendedProblem {
  problemId: number;
  problemTitle: string;
  problemTierLevel: number;
  problemTierName: string;
  problemClassLevel: number;
  recommandReasons: StudyRecommendReason[];
  tags: Tags[];
  studyMemberSolveInfo: StudyRecommendMemberSolveInfo[];
}

export interface StudyRecommendationResponse {
  problems: StudyRecommendedProblem[];
}

export interface StudyRecommendParams {
  study_id: number;
  target_user_account_id: number | null;
  recommend_all_unsolved: boolean;
  count: number;
  level: string;
  tags: string;
  exclusion_mode: string;
}

// 스터디 추천 히스토리
export interface StudyRecommendHistoryParams {
  study_id: number;
  user_account_id?: number | null;
  page?: number;
  size?: number;
}

interface StudyRecommendHistoryItemParams {
  count: number;
  exclusionMode: string;
  levelFilterCodes: string[] | null;
  tagFilterCodes: string[];
  targetUserAccountId: number | null;
  recommendAllUnsolved: boolean;
}

export interface StudyRecommendHistoryProblem {
  problemId: number;
  problemTitle: string;
  problemTierLevel: number;
  problemTierName: string;
  problemClassLevel: number;
  recommandReasons: StudyRecommendReason[];
  tags: Tags[];
}

export interface StudyRecommendHistoryItem {
  recommendationHistoryId: number;
  requesterUserAccountId: number;
  studyId: number;
  params: StudyRecommendHistoryItemParams;
  recommendedProblems: StudyRecommendHistoryProblem[];
  createdAt: string;
}

export interface StudyRecommendHistoryResponse {
  items: StudyRecommendHistoryItem[];
  hasNext: boolean;
}
