import { TierKey } from '@/shared/constants/tierSystem';

interface Target {
  targetId: number;
  targetCode: string;
  targetDisplayName: string;
}

interface UserAccount {
  userAccountId: number;
  profileImageUrl: string;
  target: Target
  registeredAt: string;
}

interface Stat {
  tierId: number;
  tierName: TierKey;
  longestStreak: number;
  rating: number;
  class: number;
  tierStartDate: string;
}

interface Streaks {
  problemHistoryId: 1;
  solvedCount: 2;
  solvedLevel: number;
  solvedDate: '2025-02-07';
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
