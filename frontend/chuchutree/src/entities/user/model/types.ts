import { TIER_INFO, TierKey } from '@/shared/constants/tierSystem';

interface Target {
  targetId: number;
  targetCode: string;
  targetDisplayName: string;
}

interface UserAccount {
  userAccountId: number;
  profileImageUrl: string;
  target: Target;
  registeredAt: string;
}

interface Stat {
  tierId: keyof typeof TIER_INFO;
  tierName: TierKey;
  longestStreak: number;
  rating: number;
  class: number;
  tierStartDate: string;
}

interface Streaks {
  problemHistoryId: number | null;
  solvedCount: number;
  solvedLevel: number;
  streakDate: string;
}

interface BjAccount {
  bjAccountId: string;
  stat: Stat;
  streaks: Streaks[];
  registeredAt: string;
}

export interface User {
  userAccount: UserAccount;
  bjAccount: BjAccount;
  linkedAt: string;
}
