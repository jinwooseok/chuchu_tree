'use client';

import { useState } from 'react';
import { BadgeCheck } from 'lucide-react';
import { CategoryTags, usePostTagBan, useDeleteTagBan } from '@/entities/tag-dashboard';
import { getLevelColorClasses, getLevelColorValue, getDaysAgo, calculateProgress, calculatePeekPosition, calculateBoxPosition, calculateMasterProgress } from '../lib/utils';
import Image from 'next/image';
import { TIER_TO_NUM } from '@/shared/constants/tierSystem';
import { CheckCircleIcon as CheckCircleIconSolid } from '@heroicons/react/24/solid'; // filled
import { CheckCircleIcon as CheckCircleIconOutline } from '@heroicons/react/24/outline'; // outline
import { CategoryName } from '@/shared/constants/tagSystem';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';
import { toast } from 'sonner';

export default function TagCard({ tag }: { tag: CategoryTags }) {
  const { tagCode, tagDisplayName, accountStat, nextLevelStat, lockedYn, excludedYn, recommendationYn, requiredStat } = tag;
  const [isAlertOpen, setIsAlertOpen] = useState(false);

  // Tag Ban mutations
  const { mutate: postTagBan, isPending: isPostPending } = usePostTagBan({
    onSuccess: () => {
      toast.success('추천 목록에서 제외되었습니다.', { position: 'top-center' });
      setIsAlertOpen(false);
    },
    onError: () => {
      toast.error('제외 처리에 실패했습니다.', { position: 'top-center' });
    },
  });

  const { mutate: deleteTagBan, isPending: isDeletePending } = useDeleteTagBan({
    onSuccess: () => {
      toast.success('추천 목록에 추가되었습니다.', { position: 'top-center' });
      setIsAlertOpen(false);
    },
    onError: () => {
      toast.error('추가 처리에 실패했습니다.', { position: 'top-center' });
    },
  });

  const isPending = isPostPending || isDeletePending;

  const handleTagBanClick = () => {
    setIsAlertOpen(true);
  };

  const handleConfirm = () => {
    if (recommendationYn) {
      // 현재 추천 중이면 제외 (Ban 추가)
      postTagBan({ tagCode });
    } else {
      // 현재 제외 중이면 추가 (Ban 삭제)
      deleteTagBan({ tagCode });
    }
  };

  // 현재 레벨과 다음 레벨
  const currentLevel = accountStat.currentLevel as CategoryName;
  const nextLevel = nextLevelStat.nextLevel;

  // 색상 클래스
  const currentLevelColors = getLevelColorClasses(currentLevel);

  // 진행률 계산
  const progress = calculateProgress({
    solvedCnt: accountStat.solvedProblemCount,
    requireSolveCnt: nextLevelStat.solvedProblemCount,
    userTier: accountStat.requiredMinTier,
    requireTier: nextLevelStat.requiredMinTier,
    highest: accountStat.higherProblemTier,
    requireHighest: nextLevelStat.higherProblemTier,
  });
  // Master 이후 진행률 계산 (최대 100)
  const masteredAfterProgress = accountStat.currentLevel !== 'MASTER' ? 0 : calculateMasterProgress({ solvedCnt: accountStat.solvedProblemCount, requireSolveCnt: nextLevelStat.solvedProblemCount });

  // 게이지 위치 계산
  const currentPeekRatio = calculatePeekPosition(progress);
  const currentBoxRatio = calculateBoxPosition(progress);
  const nextPeekRatio = accountStat.currentLevel !== 'MASTER' ? 90 : calculatePeekPosition(progress - masteredAfterProgress);
  const nextBoxRatio = accountStat.currentLevel !== 'MASTER' ? 75 : calculateBoxPosition(progress - masteredAfterProgress);

  // 마지막 풀이일
  const daysAgo = getDaysAgo(accountStat.lastSolvedDate);

  // LOCKED/EXCLUDED 상태 체크
  const isLocked = lockedYn;

  const isSuccessClear = accountStat.solvedProblemCount >= nextLevelStat.solvedProblemCount;
  const isSuccessTier = accountStat.requiredMinTier >= nextLevelStat.requiredMinTier;
  const isSuccessBest = accountStat.higherProblemTier >= nextLevelStat.higherProblemTier;

  return (
    <div className={`bg-background flex h-40 flex-col gap-2 rounded-lg p-4 text-xs`}>
      {/* 카드 헤더 */}
      <div className="flex items-center justify-between">
        <div className={`text-foreground text-sm font-semibold`}>{tagDisplayName}</div>
        <div className="flex h-full items-center justify-center gap-2">
          <div className={`text-muted-foreground flex flex-col gap-0.5`}>
            {/* Tag Ban */}
            <button
              onClick={handleTagBanClick}
              disabled={isPending}
              className={`hover:bg-excluded-bg hover:text-innerground-white border-innerground-darkgray rounded border px-2 text-center transition-colors disabled:cursor-not-allowed disabled:opacity-50`}
            >
              {recommendationYn ? '추천 포함됨' : '추천리스트 등록'}
            </button>
            <div className="flex gap-0.5">
              <p>마지막 풀이</p>
              <p className={`text-primary font-semibold`}>{daysAgo}</p>
              <p>일 전</p>
            </div>
          </div>
          <div
            className={`${!excludedYn ? currentLevelColors.bg : 'bg-excluded-bg'} ${!excludedYn ? currentLevelColors.text : 'text-innerground-white'} flex h-full items-center rounded px-2 font-semibold`}
          >
            {!excludedYn ? currentLevel : 'EXCLUDED'}
          </div>
        </div>
      </div>
      {/* 카드 바디 */}
      <div className="flex flex-1 gap-2">
        {/* 게이지 */}
        <div className="flex flex-1 items-center justify-center rounded border-2 border-dashed p-2">
          {excludedYn ? (
            <div className="flex flex-col gap-1">
              <span className="text-excluded-text text-sm font-bold">제외된 유형입니다.</span>
              <span className="text-muted-foreground text-xs">현재 {currentLevel} 상태</span>
            </div>
          ) : !isLocked ? (
            <div className="bg-innerground-darkgray relative h-4 w-full rounded-sm">
              {/* 현재 레벨 라벨 */}
              <div className={`${currentLevelColors.bg} ${currentLevelColors.text} absolute -top-6 -translate-x-1/2 rounded px-4 text-xs`} style={{ left: `${currentBoxRatio}%` }}>
                {currentLevel}
              </div>
              <div
                className="absolute bottom-full h-0 w-0 border-t-8 border-r-8 border-l-8 border-r-transparent border-l-transparent"
                style={{ left: `${currentPeekRatio - 6}%`, borderTopColor: getLevelColorValue(currentLevel) }}
              ></div>

              {/* 다음 레벨 라벨 */}
              <div className={`bg-muted-foreground text-innerground-white absolute -bottom-6 -translate-x-1/2 rounded px-4 text-xs`} style={{ left: `${nextBoxRatio}%` }}>
                {nextLevel}
              </div>
              <div
                className="border-b-muted-foreground absolute top-full h-0 w-0 border-r-8 border-b-8 border-l-8 border-r-transparent border-l-transparent"
                style={{ left: `${nextPeekRatio - 6}%` }}
              ></div>
              {/* 진행률 바 */}
              <div className={`${currentLevelColors.bg} h-4 rounded`} style={{ width: `${currentPeekRatio}%` }}></div>
            </div>
          ) : (
            <div className="flex h-full w-full items-center justify-between">
              <div className="flex h-full flex-col items-start justify-start">
                <p className="mb-2 font-semibold">추천 시작 조건</p>
                {requiredStat.prevTags.map((c) => (
                  <div key={c.tagId} className="flex w-full items-center justify-start">
                    <p>{c.tagDisplayName}</p>
                    <div className="ml-2">
                      <BadgeCheck height={12} width={12} />
                    </div>
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
                <p className="mb-2 font-semibold">최소 달성 티어</p>
                <Image src={`/tiers/tier_${TIER_TO_NUM[requiredStat.requiredMinTier]}.svg`} alt={`Tier ${TIER_TO_NUM[requiredStat.requiredMinTier]}`} width={24} height={24} className="h-8 w-8" />
              </div>
            </div>
          )}
        </div>
        {/* 스탯 */}
        <div className="flex flex-col gap-2 rounded border-2 border-dashed px-1 py-2">
          <div className="flex items-center justify-between gap-4">
            <div>Clear</div>
            <div className={`${excludedYn ? 'text-excluded-text' : isSuccessClear ? 'text-advanced-bg font-semibold' : 'text-muted-foreground'} flex items-center justify-center`}>
              <p>{accountStat.solvedProblemCount}</p>
              <p>/</p>
              <p>{nextLevelStat.solvedProblemCount}</p>
              <div className="ml-2">{isSuccessClear ? <CheckCircleIconSolid height={12} width={12} /> : <CheckCircleIconOutline height={12} width={12} />}</div>
            </div>
          </div>
          <div className="flex items-center justify-between gap-4">
            <div>Tier</div>
            <div className={`${excludedYn ? 'text-excluded-text' : isSuccessTier ? 'text-advanced-bg font-semibold' : 'text-muted-foreground'} flex items-center justify-center`}>
              <p>{nextLevelStat.requiredMinTier}</p>
              <div className="ml-2">{isSuccessTier ? <CheckCircleIconSolid height={12} width={12} /> : <CheckCircleIconOutline height={12} width={12} />}</div>
            </div>
          </div>
          <div className="flex items-center justify-between gap-4">
            <div>Best</div>
            <div className={`${excludedYn ? 'text-excluded-text' : isSuccessBest ? 'text-advanced-bg font-semibold' : 'text-muted-foreground'} flex items-center justify-center`}>
              <p>{accountStat.higherProblemTier}</p>
              <p>/</p>
              <p>{nextLevelStat.higherProblemTier}</p>
              <div className="ml-2">{isSuccessBest ? <CheckCircleIconSolid height={12} width={12} /> : <CheckCircleIconOutline height={12} width={12} />}</div>
            </div>
          </div>
        </div>
      </div>

      {/* Tag Ban Alert Dialog */}
      <AlertDialog open={isAlertOpen} onOpenChange={setIsAlertOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>
              {recommendationYn ? '추천 목록에서 제외하시겠습니까?' : '추천 목록에 추가하시겠습니까?'}
            </AlertDialogTitle>
            <AlertDialogDescription>
              {recommendationYn
                ? `"${tagDisplayName}" 유형을 추천 목록에서 제외합니다. 제외된 유형은 문제 추천 시 포함되지 않습니다.`
                : `"${tagDisplayName}" 유형을 추천 목록에 추가합니다. 이 유형의 문제가 추천될 수 있습니다.`}
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={isPending}>취소</AlertDialogCancel>
            <AlertDialogAction onClick={handleConfirm} disabled={isPending}>
              {isPending ? '처리 중...' : recommendationYn ? '제외하기' : '추가하기'}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
