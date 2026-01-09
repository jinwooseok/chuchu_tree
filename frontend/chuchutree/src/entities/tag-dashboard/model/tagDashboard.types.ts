import { CategoryName, TagKey, TargetCode } from '@/shared/constants/tagSystem';
import { TierKey, TierNumKey } from '@/shared/constants/tierSystem';

interface TagTargets {
  targetId: number;
  targetCode: TargetCode;
  targetDisplayName: string;
}

interface TagAliases {
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
    requiredMinTier: TierKey;
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
  };
  lockedYn: boolean;
  excludedYn: boolean;
  recommendationYn: boolean;
}

interface CategoryInfoTags {
  tagId: number;
  tagCode: TagKey;
  tagDisplayName: string;
}

interface Categories {
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
