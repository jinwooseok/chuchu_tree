import { useUser } from '@/entities/user/model/queries';
import { TIER_INFO, TierNumKey } from '@/shared/constants/tierSystem';

const masterId: number = 31;

export default function TopTierbar() {
  const { data: user } = useUser();

  if (!user) return null;

  const tierId = user.bjAccount.stat.tierId;
  const rating = user.bjAccount.stat.rating;
  const nextTierId: TierNumKey = tierId === masterId ? tierId : ((tierId + 1) as TierNumKey);
  const ratingToNext = TIER_INFO[nextTierId].rating - Number(rating);
  const totalRatingForNextTier = TIER_INFO[nextTierId].rating - TIER_INFO[tierId].rating;
  const tierRatio = ((totalRatingForNextTier - ratingToNext) / totalRatingForNextTier) * 100;

  return (
    <div className="bg-innerground-white flex h-full flex-col items-center justify-center gap-2 p-6">
      <div className="flex w-full justify-between">
        <div className="flex items-center justify-center gap-1">
          <h3 className="text-sm">{TIER_INFO[tierId].name}</h3>
          <h3 className="text-sm">{TIER_INFO[tierId].num}</h3>
          <h3 className="text-sm">{rating}</h3>
        </div>
        <div className="flex items-center justify-center gap-1">
          <p className="text-muted-foreground text-xs">{TIER_INFO[nextTierId].name}</p>
          <p className="text-muted-foreground text-xs">{TIER_INFO[nextTierId].num} 승급까지</p>
          <p className="text-muted-foreground text-xs">-{ratingToNext}</p>
        </div>
      </div>
      <div className="bg-foreground h-6 w-full rounded-sm">
        <div className={`${TIER_INFO[tierId].bgColor} h-6 rounded`} style={{ width: `${tierRatio}%` }}></div>
      </div>
    </div>
  );
}
