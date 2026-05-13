import { CategoryName, TagKey, TargetCode } from '@/shared/constants/tagSystem';
import { TierKey, TierNumKey } from '@/shared/constants/tierSystem';

export interface TagTargets {
  targetId: number;
  targetCode: TargetCode;
  targetDisplayName: string;
}

export interface TagAliases {
  alias: string;
}

interface PrevTags {
  tagId: number;
  tagCode: TagKey;
  tagDisplayName: string;
  satisfiedYn: boolean;
}

export interface CategoryTags {
  tagId: number;
  tagCode: TagKey;
  tagDisplayName: string;
  tagTargets: TagTargets[];
  tagAliases: TagAliases[];
  requiredStat: {
    requiredMinTier: TierNumKey;
    prevTags: PrevTags[];
  };
  nextLevelStat: {
    nextLevel: CategoryName;
    solvedProblemCount: number;
    requiredMinTier: TierNumKey;
    higherProblemTier: TierNumKey;
  };
  accountStat: {
    currentLevel: CategoryName;
    solvedProblemCount: number;
    requiredMinTier: TierNumKey;
    higherProblemTier: TierNumKey;
    lastSolvedDate: string;
    recommendation_period: number;
  };
  lockedYn: boolean;
  excludedYn: boolean;
  recommendationYn: boolean;
}

export interface CategoryInfoTags {
  tagId: number;
  tagCode: TagKey;
  tagDisplayName: string;
}

export interface Categories {
  categoryName: CategoryName;
  tags: CategoryInfoTags[];
}

export interface TagDashboard {
  categories: Categories[];
  tags: CategoryTags[];
}

// 태그 밴

export interface TagBan {
  tagCode: TagKey;
}

// 태그 디테일

export interface TagDetailTag {
  tagId: number;
  tagCode: TagKey;
  tagDisplayName: string;
  tagAliases: TagAliases[];
  tagTargets: TagTargets[];
}

export interface TagDetailProblem {
  problemId: number;
  problemTitle: string;
  problemTierLevel: number;
  problemTierName: TierKey;
  problemClassLevel: number | null;
  tags: TagDetailTag[];
  solvedDate: string | null;
}

export interface TagDetail {
  totalProblemCount: number;
  problems: TagDetailProblem[];
}
