import { User } from '@/entities/user';
import { getTierDetail } from '@/features/top-tierbar/lib/utils';

export default function Tierbar({ user }: { user: User }) {
  const tierDetail = getTierDetail(user);

  return (
    <div className="flex w-full cursor-default flex-col items-center justify-center gap-2">
      <div className="flex w-full justify-between">
        <div className="flex items-center justify-center gap-1">
          <h3 className="text-sm">{tierDetail.tierName}</h3>
          <h3 className="text-sm">{tierDetail.tierNum}</h3>
          <h3 className="text-sm">{tierDetail.rowRating}</h3>
        </div>
        <div className="flex items-center justify-center gap-1">
          <p className="text-muted-foreground text-xs">{tierDetail.nextName}</p>
          <p className="text-muted-foreground text-xs">{tierDetail.nextNum} 승급까지</p>
          <p className="text-muted-foreground text-xs">-{tierDetail.rowRatingToNext}</p>
        </div>
      </div>
      <div className="bg-foreground h-6 w-full rounded-sm">
        <div className={`${tierDetail.tierBgColor} h-6 rounded`} style={{ width: `${tierDetail.rowTierRatio}%` }}></div>
      </div>
    </div>
  );
}
