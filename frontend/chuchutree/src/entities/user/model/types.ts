import { TargetCode } from '@/shared/constants/tagSystem';
import { TierKey, TierNumKey } from '@/shared/constants/tierSystem';

interface Target {
  targetId: number;
  targetCode: string;
  targetDisplayName: string;
}

interface UserAccount {
  userAccountId: number;
  profileImageUrl: string | null;
  target: Target;
  registeredAt: string;
  isSynced: boolean;
}

interface Stat {
  tierId: TierNumKey;
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

// 목표 설정/변경

export interface PostTargetType {
  targetCode: TargetCode;
}

// 추가 스트릭 get

export interface Streak {
  bjAccountId: string;
  streaks: Streaks[];
}
