// Tag Dashboard 관련 타입 정의

import { TierKey } from '@/shared/constants/tierSystem';

export interface PrevTag {
  tagId: number;
  tagCode: string;
  tagDisplayName: string;
  satisfiedYn: boolean;
}

export interface RequiredStat {
  requiredMinTier: TierKey;
  prevTags: PrevTag[];
}

export interface NextLevelStat {
  nextLevel: string;
  solvedProblemCount: number;
  requiredMinTier: TierKey;
  higherProblemTier: TierKey;
}

export interface AccountStat {
  currentLevel: string;
  solvedProblemCount: number;
  requiredMinTier: TierKey;
  higherProblemTier: TierKey;
  lastSolvedDate: string; // YYYY-MM-DD 형식
}

export interface TagDetail {
  tagId: number;
  tagCode: string;
  tagDisplayName: string;
  requiredStat: RequiredStat;
  nextLevelStat: NextLevelStat;
  accountStat: AccountStat;
  locked_yn: boolean;
  excluded_yn: boolean;
  recommandation_yn: boolean;
}

export interface CategoryTag {
  tagId: number;
  tagCode: string;
  tagDisplayName: string;
}

export interface Category {
  categoryName: TagLevel;
  tags: CategoryTag[];
}

export interface TagDashboardApiResponse {
  status: number;
  message: string;
  data: {
    categories: Category[];
    tags: TagDetail[];
  };
  error: Record<string, any>;
}

// 레벨 타입
export type TagLevel = 'IMEDIATED' | 'ADVANCED' | 'MASTER' | 'LOCKED' | 'EXCLUDED';
