import { TierNumKey } from '@/shared/constants/tierSystem';
import { CategoryName } from '@/shared/constants/tagSystem';

// 레벨별 색상 클래스 반환
export function getLevelColorClasses(level: CategoryName): { bg: string; text: string; border: string; borderTop: string; short: string } {
  switch (level) {
    case 'INTERMEDIATE':
      return { bg: 'bg-intermediate-bg', text: 'text-intermediate-text', border: 'border-intermediate-bg', borderTop: 'border-t-intermediate-bg', short: 'I' };
    case 'ADVANCED':
      return { bg: 'bg-advanced-bg', text: 'text-advanced-text', border: 'border-advanced-bg', borderTop: 'border-t-advanced-bg', short: 'A' };
    case 'MASTER':
      return { bg: 'bg-master-bg', text: 'text-master-text', border: 'border-master-bg', borderTop: 'border-t-master-bg', short: 'M' };
    case 'LOCKED':
      return { bg: 'bg-locked-bg', text: 'text-locked-text', border: 'border-locked-bg', borderTop: 'border-t-locked-bg', short: 'L' };
    case 'EXCLUDED':
      return { bg: 'bg-excluded-bg', text: 'text-excluded-text', border: 'border-excluded-bg', borderTop: 'border-t-excluded-bg', short: 'EX' };
    default:
      return { bg: 'bg-gray-300', text: 'text-gray-700', border: 'border-gray-300', borderTop: 'border-t-gray-300', short: 'D' };
  }
}

// 날짜로부터 며칠 전인지 계산
export function getDaysAgo(dateString: string): number {
  const targetDate = new Date(dateString);
  targetDate.setHours(0, 0, 0, 0);

  const today = new Date();
  today.setHours(0, 0, 0, 0);

  const diffTime = today.getTime() - targetDate.getTime();
  const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));

  return Math.max(0, diffDays); // 미래 날짜는 0으로 처리
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
  userTier: TierNumKey;
  requireTier: TierNumKey;
  highest: TierNumKey;
  requireHighest: TierNumKey;
}) {
  const solvedPoint = Math.min(60, Math.round((solvedCnt / requireSolveCnt) * 60));
  const userTierNum = Math.max(0, requireTier - userTier);
  const userTierPoint = userTierNum >= 3 ? 0 : userTierNum === 2 ? 10 : userTierNum === 1 ? 20 : 30;
  const highestPoint = requireHighest <= highest ? 10 : 0;
  return solvedPoint + userTierPoint + highestPoint;
}

// 게이지 포인터 위치 계산
export function calculatePeekPosition(ratio: number): number {
  return Math.round((ratio * 80) / 100) + 10;
}

// 게이지 박스 위치 계산
export function calculateBoxPosition(ratio: number, name: CategoryName): number {
  const len = name.length;
  return Math.round((ratio * 80) / 100) + 10 + ((50 - ratio) / 100) * len * 2.3;
}
