'use client';

import streakData from '../mock/bj-accounts_streak_260126.json';

interface StreakItem {
  problemHistoryId: number | null;
  streakDate: string;
  solvedCount: number;
  solvedLevel: number;
}

/**
 * 랜딩페이지용 스트릭 데이터 훅
 * 통합된 JSON의 전체 streak 데이터를 반환
 */
export function useLandingStreak(): StreakItem[] {
  return streakData.data.streaks;
}
