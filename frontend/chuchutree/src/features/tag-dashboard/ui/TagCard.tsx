'use client';

import { CategoryTags, usePostTagBan, useDeleteTagBan } from '@/entities/tag-dashboard';
import { getLevelColorClasses, getDaysAgo } from '../lib/utils';
import Image from 'next/image';
import { CheckCircleIcon as CheckCircleIconSolid } from '@heroicons/react/24/solid'; // filled
import { CheckCircleIcon as CheckCircleIconOutline } from '@heroicons/react/24/outline'; // outline
import { toast } from 'sonner';
import { useModal } from '@/lib/providers/modal-provider';
import { TagBanAlertDialog } from './TagBanAlertDialog';
import TagCardProgressBar from '@/features/tag-dashboard/ui/TagCardProgressBar';
import { AppTooltip } from '@/components/custom/tooltip/AppTooltip';
import { TIER_INFO } from '@/shared/constants/tierSystem';

export default function TagCard({ tag }: { tag: CategoryTags }) {
  const { tagCode, tagDisplayName, accountStat, nextLevelStat, excludedYn, recommendationYn } = tag;
  const { openModal, closeModal } = useModal();

  // Tag Ban mutations
  const { mutate: postTagBan, isPending: isPostPending } = usePostTagBan({
    onSuccess: () => {
      toast.success('추천 목록에서 제외되었습니다.', { position: 'top-center' });
      closeModal('tag-ban-alert');
    },
    onError: () => {
      toast.error('제외 처리에 실패했습니다.', { position: 'top-center' });
    },
  });

  const { mutate: deleteTagBan, isPending: isDeletePending } = useDeleteTagBan({
    onSuccess: () => {
      toast.success('추천 목록에 추가되었습니다.', { position: 'top-center' });
      closeModal('tag-ban-alert');
    },
    onError: () => {
      toast.error('추가 처리에 실패했습니다.', { position: 'top-center' });
    },
  });

  const isPending = isPostPending || isDeletePending;

  const handleConfirm = () => {
    if (recommendationYn) {
      // 현재 추천 중이면 제외 (Ban 추가)
      postTagBan({ tagCode });
    } else {
      // 현재 제외 중이면 추가 (Ban 삭제)
      deleteTagBan({ tagCode });
    }
  };

  const handleTagBanClick = () => {
    openModal(
      'tag-ban-alert',
      <TagBanAlertDialog tagDisplayName={tagDisplayName} recommendationYn={recommendationYn} isPending={isPending} onConfirm={handleConfirm} onClose={() => closeModal('tag-ban-alert')} />,
    );
  };

  // 색상 클래스
  const currentLevelColors = getLevelColorClasses(accountStat.currentLevel);

  // 마지막 풀이일
  const daysAgo = getDaysAgo(accountStat.lastSolvedDate);

  // LOCKED/EXCLUDED 상태 체크
  const isSuccessClear = accountStat.solvedProblemCount >= nextLevelStat.solvedProblemCount;
  const isSuccessTier = accountStat.requiredMinTier >= nextLevelStat.requiredMinTier;
  const isSuccessBest = accountStat.higherProblemTier >= nextLevelStat.higherProblemTier;

  return (
    <div
      className={`bg-background flex flex-col gap-2 rounded-lg border-3 ${!excludedYn ? currentLevelColors.border : 'border-excluded-bg'} group relative w-80 p-4 text-xs transition-all duration-100 ease-in-out hover:shadow-md`}
    >
      {/* 우상단 */}
      <div className="absolute top-0 right-0 overflow-hidden">
        <div
          className={`${!excludedYn ? currentLevelColors.bg : 'bg-excluded-bg'} text-innerground-white translate-x-full rounded-bl-lg px-2 text-center font-semibold transition-transform duration-300 ease-out group-hover:translate-x-0`}
        >
          {!excludedYn ? accountStat.currentLevel : 'EXCLUDED'}
        </div>
      </div>
      {/* 카드 헤더 */}
      <div className="flex items-center justify-between">
        <div className={`text-foreground text-sm font-semibold`}>{tagDisplayName}</div>
        <div className="flex h-full items-center justify-center gap-2">
          <div className={`text-muted-foreground flex flex-col gap-0.5`}>
            {/* Tag Ban */}
            <AppTooltip side="bottom" content={recommendationYn ? '추천 목록에서 제외' : '추천 목록에 추가'}>
              <button
                onClick={handleTagBanClick}
                aria-label="추천 여부 토글버튼"
                disabled={isPending}
                className={`hover:bg-excluded-bg hover:text-innerground-white border-innerground-darkgray rounded border px-2 text-center transition-colors disabled:cursor-not-allowed disabled:opacity-50`}
              >
                {recommendationYn ? '추천 포함됨' : '추천 제외됨'}
              </button>
            </AppTooltip>
            {accountStat.lastSolvedDate !== null ? (
              <div className="flex gap-0.5">
                <p>마지막 풀이</p>
                <p className={`text-primary font-semibold`}>{daysAgo}</p>
                <p>일 전</p>
              </div>
            ) : accountStat.solvedProblemCount === 0 ? (
              <div className="flex gap-0.5">
                <p>풀어본 적</p>
                <p className={`text-primary font-semibold`}>없는</p>
                <p>유형</p>
              </div>
            ) : (
              <div className="flex gap-0.5">
                <p>가입</p>
                <p className={`text-primary font-semibold`}>전</p>
                <p>풀이</p>
              </div>
            )}
          </div>
        </div>
      </div>
      {/* 게이지 */}
      <TagCardProgressBar tag={tag} />
      {/* 스탯 */}
      <div className="flex cursor-default flex-col gap-2 rounded border-2 border-dashed px-1 py-2">
        <div className="flex items-center justify-between gap-4">
          <AppTooltip content="다음 등급을 위한 문제 수" side="right">
            <div>풀이 수</div>
          </AppTooltip>

          <div className={`${excludedYn ? 'text-excluded-text' : isSuccessClear ? 'text-advanced-bg font-semibold' : 'text-muted-foreground'} flex items-center justify-center`}>
            <p>{accountStat.solvedProblemCount}</p>
            <p>/</p>
            <p>{nextLevelStat.solvedProblemCount} 문제</p>
            <div className="ml-2" aria-label={isSuccessClear ? '풀이 수 달성' : '풀이 수 미달성'}>
              {isSuccessClear ? <CheckCircleIconSolid height={12} width={12} aria-hidden="true" /> : <CheckCircleIconOutline height={12} width={12} aria-hidden="true" />}
            </div>
          </div>
        </div>
        <div className="flex items-center justify-between gap-4">
          <AppTooltip content="다음 등급을 위한 사용자 티어" side="right">
            <div>최소 달성 티어</div>
          </AppTooltip>
          <div className={`${excludedYn ? 'text-excluded-text' : isSuccessTier ? 'text-advanced-bg font-semibold' : 'text-muted-foreground'} flex items-center justify-center`}>
            <Image src={`/tiers/tier_${nextLevelStat.requiredMinTier}.svg`} alt={`Tier ${nextLevelStat.requiredMinTier}`} width={12} height={12} className="h-4 w-4" />
            <div className="ml-2" aria-label={isSuccessTier ? '최소 티어 달성' : '최소 티어 미달성'}>
              {isSuccessTier ? <CheckCircleIconSolid height={12} width={12} aria-hidden="true" /> : <CheckCircleIconOutline height={12} width={12} aria-hidden="true" />}
            </div>
          </div>
        </div>
        <div className="flex items-center justify-between gap-4">
          <AppTooltip content="다음 등급을 위한 목표 문제 티어" side="right">
            <div>최고 난이도</div>
          </AppTooltip>

          <div className={`${excludedYn ? 'text-excluded-text' : isSuccessBest ? 'text-advanced-bg font-semibold' : 'text-muted-foreground'} flex items-center justify-center`}>
            {accountStat.higherProblemTier === null ? <p>0</p> : <p>{TIER_INFO[accountStat.higherProblemTier].short}</p>}
            <p>/</p>
            <p>{TIER_INFO[nextLevelStat.higherProblemTier].short}</p>
            <div className="ml-2" aria-label={isSuccessBest ? '최고 난이도 달성' : '최고 난이도 미달성'}>
              {isSuccessBest ? <CheckCircleIconSolid height={12} width={12} aria-hidden="true" /> : <CheckCircleIconOutline height={12} width={12} aria-hidden="true" />}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
