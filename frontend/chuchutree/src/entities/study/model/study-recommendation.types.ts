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
}
