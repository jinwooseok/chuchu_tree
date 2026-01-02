import { TIER_TO_NUM, TierKey } from '@/shared/constants/tierSystem';
import { TagLevel } from '@/shared/types/tagDashboard';

// 레벨별 색상 클래스 반환
export function getLevelColorClasses(level: TagLevel): { bg: string; text: string } {
  switch (level) {
    case 'IMEDIATED':
      return { bg: 'bg-imediated-bg', text: 'text-imediated-text' };
    case 'ADVANCED':
      return { bg: 'bg-advanced-bg', text: 'text-advanced-text' };
    case 'MASTER':
      return { bg: 'bg-master-bg', text: 'text-master-text' };
    case 'LOCKED':
      return { bg: 'bg-locked-bg', text: 'text-locked-text' };
    case 'EXCLUDED':
      return { bg: 'bg-excluded-bg', text: 'text-excluded-text' };
    default:
      return { bg: 'bg-gray-300', text: 'text-gray-700' };
  }
}

// 레벨별 색상 값 반환 (inline style용)
export function getLevelColorValue(level: TagLevel): string {
  switch (level) {
    case 'IMEDIATED':
      return '#f9b473';
    case 'ADVANCED':
      return '#79ab7c';
    case 'MASTER':
      return '#47c6f9';
    case 'LOCKED':
      return '#e4e4e4';
    case 'EXCLUDED':
      return '#ed6e6e';
    default:
      return '#d1d5db';
  }
}

// 날짜로부터 며칠 전인지 계산
export function getDaysAgo(dateString: string): number {
  const lastDate = new Date(dateString);
  const today = new Date();
  const diffTime = Math.abs(today.getTime() - lastDate.getTime());
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  return diffDays;
}

// 진행률 계산 (0-100)
export function calculateProgress({
  solvedCnt,
  requireSolveCnt,
  userTier,
  requireTier,
  highest,
  requireHighest,
}: {
  solvedCnt: number;
  requireSolveCnt: number;
  userTier: TierKey;
  requireTier: TierKey;
  highest: TierKey;
  requireHighest: TierKey;
}) {
  const solvedPoint = Math.min(60, Math.round((solvedCnt / requireSolveCnt) * 60));
  const userTierNum = Math.max(0, TIER_TO_NUM[requireTier] - TIER_TO_NUM[userTier]);
  const userTierPoint = userTierNum >= 3 ? 0 : userTierNum === 2 ? 10 : userTierNum === 1 ? 20 : 30;
  const highestPoint = TIER_TO_NUM[requireHighest] <= TIER_TO_NUM[highest] ? 10 : 0;
  return solvedPoint + userTierPoint + highestPoint;
}

// 게이지 박스 위치 계산 (10-90 범위로 제한)
export function calculatePeekPosition(ratio: number): number {
  return Math.round((ratio * 80) / 100) + 10;
}

// 게이지 박스 위치 계산 (25-75 범위로 제한)
export function calculateBoxPosition(ratio: number): number {
  return ratio > 75 ? 75 : ratio < 25 ? 25 : ratio;
}

// Master 이후 진행률 계산 (0-100)
export function calculateMasterProgress({ solvedCnt, requireSolveCnt }: { solvedCnt: number; requireSolveCnt: number }) {
  const solvedMasterPoint = Math.min(100, (solvedCnt - requireSolveCnt) * 10);
  return solvedMasterPoint;
}
