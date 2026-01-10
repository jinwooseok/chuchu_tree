import { CategoryTags } from '@/entities/tag-dashboard';
import { calculateBoxPosition, calculatePeekPosition, calculateProgress, getLevelColorClasses } from '@/features/tag-dashboard/lib/utils';
import Image from 'next/image';
import { CheckCircleIcon as CheckCircleIconSolid } from '@heroicons/react/24/solid'; // filled
import { CheckCircleIcon as CheckCircleIconOutline } from '@heroicons/react/24/outline'; // outline
import { BadgeCheck } from 'lucide-react';

export default function TagCardProgressBar({ tag }: { tag: CategoryTags }) {
  const { accountStat, nextLevelStat, lockedYn, excludedYn, requiredStat } = tag;
  const currentLevelColors = getLevelColorClasses(accountStat.currentLevel);
  // 진행률 계산
  const progress = calculateProgress({
    solvedCnt: accountStat.solvedProblemCount,
    requireSolveCnt: nextLevelStat.solvedProblemCount,
    userTier: accountStat.requiredMinTier,
    requireTier: nextLevelStat.requiredMinTier,
    highest: accountStat.higherProblemTier,
    requireHighest: nextLevelStat.higherProblemTier,
  });

  // 게이지 위치 계산
  const currentPeekRatio = calculatePeekPosition(progress);
  const currentBoxRatio = calculateBoxPosition(progress, accountStat.currentLevel);
  const nextPeekRatio = calculatePeekPosition(100);
  const nextBoxRatio = calculateBoxPosition(100, accountStat.currentLevel);
  // 시작티어 달성여부
  const isStartTier = accountStat.requiredMinTier >= requiredStat.requiredMinTier;
  if (excludedYn) {
    return (
      <div className="flex min-h-18 flex-1 items-center justify-center rounded border-2 border-dashed p-2">
        <div className="flex flex-col gap-1">
          <span className="text-excluded-text text-sm font-bold">제외된 유형입니다.</span>
          <span className="text-muted-foreground text-xs">현재 {accountStat.currentLevel} 상태</span>
        </div>
      </div>
    );
  } else if (lockedYn) {
    return (
      <div className="flex min-h-18 flex-1 items-center justify-center rounded border-2 border-dashed p-2">
        <div className="flex h-full w-full items-center justify-between">
          <div className="flex h-full flex-col items-start justify-start">
            <p className="mb-2 font-semibold">추천 시작 조건</p>
            {requiredStat.prevTags.map((c) => (
              <div key={c.tagId} className={`flex w-full items-center justify-start ${excludedYn ? 'text-excluded-text' : c.satisfiedYn ? 'text-advanced-bg font-semibold' : 'text-muted-foreground'}`}>
                <p>{c.tagDisplayName}</p>
                <div className="ml-2">{c.satisfiedYn ? <CheckCircleIconSolid height={12} width={12} /> : <CheckCircleIconOutline height={12} width={12} />}</div>
              </div>
            ))}
            {requiredStat.prevTags.length === 0 ? (
              <div className="flex h-full w-full items-center justify-center">
                <div className="ml-2">
                  <BadgeCheck height={16} width={16} />
                </div>
              </div>
            ) : null}
          </div>
          <div className="flex h-full flex-col items-center justify-start">
            <p className="mb-2 font-semibold">최소 시작 티어</p>
            <div className={`flex items-center justify-center ${excludedYn ? 'text-excluded-text' : isStartTier ? 'text-advanced-bg font-semibold' : 'text-muted-foreground'}`}>
              <Image src={`/tiers/tier_${requiredStat.requiredMinTier}.svg`} alt={`Tier ${requiredStat.requiredMinTier}`} width={24} height={24} className="h-8 w-8" />
              <div className="ml-2">{isStartTier ? <CheckCircleIconSolid height={12} width={12} /> : <CheckCircleIconOutline height={12} width={12} />}</div>
            </div>
          </div>
        </div>
      </div>
    );
  } else if (accountStat.currentLevel === 'MASTER') {
    return (
      <div className="flex min-h-18 flex-1 flex-col items-center justify-center gap-1 rounded border-2 border-dashed p-2">
        <span className="text-master-text text-sm font-bold">마스터한 유형입니다.</span>
        <span className="text-muted-foreground text-xs">가끔 추천 될 수 있습니다.</span>
      </div>
    );
  } else {
    return (
      <div className="flex min-h-18 flex-1 items-center justify-center rounded border-2 border-dashed p-2">
        <div className="bg-innerground-darkgray relative h-2 w-full rounded-sm">
          {/* 현재 레벨 라벨 */}
          <div className={`${currentLevelColors.bg} ${currentLevelColors.text} absolute -top-6 -translate-x-1/2 rounded px-4 text-xs`} style={{ left: `calc(${currentBoxRatio}% )` }}>
            {accountStat.currentLevel}
          </div>
          <div
            className={`absolute bottom-full h-0 w-0 border-t-8 border-r-8 border-l-8 border-r-transparent border-l-transparent ${currentLevelColors.borderTop}`}
            style={{ left: `calc(${currentPeekRatio}% - 10px)` }}
          ></div>

          {/* 다음 레벨 라벨 */}
          <div className={`bg-muted-foreground text-innerground-white absolute -bottom-6 -translate-x-1/2 rounded px-4 text-xs`} style={{ left: `calc(${nextBoxRatio}% )` }}>
            {nextLevelStat.nextLevel}
          </div>
          <div
            className="border-b-muted-foreground absolute top-full h-0 w-0 border-r-8 border-b-8 border-l-8 border-r-transparent border-l-transparent"
            style={{ left: `calc(${nextPeekRatio}% - 10px)` }}
          ></div>
          {/* 진행률 바 */}
          <div className="bg-innerground-darkgray relative h-2 w-full overflow-hidden rounded-sm">
            <div className={`${currentLevelColors.bg} animate-in slide-in-from-left h-2 rounded transition-all duration-2000 ease-out`} style={{ width: `${currentPeekRatio}%` }}></div>
          </div>
        </div>
      </div>
    );
  }
}
