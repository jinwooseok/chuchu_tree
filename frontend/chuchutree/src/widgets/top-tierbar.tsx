import { TIER_INFO } from '@/shared/constants/tierSystem';
type TierKey = keyof typeof TIER_INFO;

const MockUserInfoTierId = '17';
const MockUserInfoRating = '1859';

export default function TopTierbar() {
  const masterId: string = '31';
  const nextTierId: TierKey = MockUserInfoTierId === masterId ? MockUserInfoTierId : ((Number(MockUserInfoTierId) + 1).toString() as TierKey);
  const ratingToNext = TIER_INFO[nextTierId].rating - Number(MockUserInfoRating);
  const totalRatingForNextTier = TIER_INFO[nextTierId].rating - TIER_INFO[MockUserInfoTierId].rating;
  const tierRatio = ((totalRatingForNextTier - ratingToNext) / totalRatingForNextTier) * 100;
  return (
    <div className="bg-innerground-white flex h-full flex-col items-center justify-center gap-2 p-6">
      <div className="flex w-full justify-between">
        <div className="flex items-center justify-center gap-1">
          <h3 className="text-sm">{TIER_INFO[MockUserInfoTierId].name}</h3>
          <h3 className="text-sm">{TIER_INFO[MockUserInfoTierId].num}</h3>
          <h3 className="text-sm">{MockUserInfoRating}</h3>
        </div>
        <div className="flex items-center justify-center gap-1">
          <p className="text-muted-foreground text-xs">{TIER_INFO[nextTierId].name}</p>
          <p className="text-muted-foreground text-xs">{TIER_INFO[nextTierId].num} 승급까지</p>
          <p className="text-muted-foreground text-xs">-{ratingToNext}</p>
        </div>
      </div>
      <div className="bg-foreground h-6 w-full rounded-sm">
        <div className={`${TIER_INFO[MockUserInfoTierId].bgColor} h-6 rounded`} style={{ width: `${tierRatio}%` }}></div>
      </div>
    </div>
  );
}
