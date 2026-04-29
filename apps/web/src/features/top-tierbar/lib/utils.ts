import { User } from '@/entities/user';
import { TIER_INFO, TierNumKey } from '@/shared/constants/tierSystem';

const masterId: number = 31; // 마스터 티어

interface TierDetail {
  rowTierId: TierNumKey;
  rowRating: number;
  rowNextTierId: TierNumKey;
  rowRatingToNext: number;
  rowTotalRatingForNextTier: number;
  rowTierRatio: number;
  tierName: string;
  tierNum: string;
  nextName: string;
  nextNum: string;
  tierBgColor: string;
}

export function getTierDetail(user: User): TierDetail {
  const tierId = user.bjAccount.stat.tierId;
  const rating = user.bjAccount.stat.rating;
  const nextTierId: TierNumKey = tierId === masterId ? tierId : ((tierId + 1) as TierNumKey);
  const ratingToNext = TIER_INFO[nextTierId].rating - Number(rating);
  const totalRatingForNextTier = TIER_INFO[nextTierId].rating - TIER_INFO[tierId].rating;
  const tierRatio = ((totalRatingForNextTier - ratingToNext) / totalRatingForNextTier) * 100;
  return {
    rowTierId: tierId, // 현재 티어
    rowRating: rating, // 현재 레이팅 점수
    rowNextTierId: nextTierId, // 다음 티어
    rowRatingToNext: ratingToNext, // 다음티어까지 남은 레이팅 점수
    rowTotalRatingForNextTier: totalRatingForNextTier, // 승급을 위한 총 레이팅 점수
    rowTierRatio: tierRatio, // 다음티어까지 남은 레이팅 점수의 비율
    tierName: TIER_INFO[tierId].name,
    tierNum: TIER_INFO[tierId].num,
    nextName: TIER_INFO[nextTierId].name,
    nextNum: TIER_INFO[nextTierId].num,
    tierBgColor: TIER_INFO[tierId].bgColor,
  };
}
