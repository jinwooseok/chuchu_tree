import { TagKey } from '@/shared/constants/tagSystem';
import { TierKey, TierNumKey } from '@/shared/constants/tierSystem';

interface TagTargets {
  targetId: number;
  targetCode: string;
  targetDisplayName: string;
}

interface TagAliases {
  alias: string;
}

interface Tags {
  tagId: number;
  tagCode: TagKey;
  tagDisplayName: string;
  tagTargets: TagTargets[];
  tagAliases: TagAliases[];
}

interface RecommandReasons {
  reason: string;
  additionalData: string;
}

interface RecommendedProblems {
  problemId: number;
  problemTitle: string;
  problemTierLevel: TierNumKey;
  problemTierName: TierKey;
  problemClassLevel: number;
  recommandReasons: RecommandReasons[];
  tags: Tags[];
}

export interface Recommendation {
  problems: RecommendedProblems[];
}

// 문제 밴
export interface BanProblem {
  problemId: number;
}
