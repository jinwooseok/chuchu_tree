'use client';

import { CategoryTags, useTagDetail } from '@/entities/tag-dashboard';
import { getLevelColorClasses, getDaysAgo } from '../lib/utils';
import { TAG_INFO } from '@/shared/constants/tagSystem';
import { TIER_INFO } from '@/shared/constants/tierSystem';
import Image from 'next/image';

type TagWithProgress = CategoryTags & { progress: number };

interface TagDetailCardProps {
  tag: TagWithProgress;
}

export function TagDetailCard({ tag }: TagDetailCardProps) {
  // useQuery: 캐싱 적용 - 이미 조회한 태그는 재요청 없이 즉시 표시
  const { data: tagDetail, isPending, isError } = useTagDetail(tag.tagCode);

  const currentLevelColors = getLevelColorClasses(tag.excludedYn ? 'EXCLUDED' : tag.lockedYn ? 'LOCKED' : tag.accountStat.currentLevel);

  // solvedDate 내림차순 정렬 (가장 최신 풀이 먼저, null은 맨 뒤)
  const sortedProblems = tagDetail
    ? [...tagDetail.problems].sort((a, b) => {
        if (a.solvedDate === null && b.solvedDate === null) return 0;
        if (a.solvedDate === null) return 1;
        if (b.solvedDate === null) return -1;
        return new Date(b.solvedDate).getTime() - new Date(a.solvedDate).getTime();
      })
    : [];

  return (
    // h-full w-full: 그리드 셀 높이(= TagCard 높이)를 꽉 채움
    // overflow-hidden: 내부 콘텐츠가 카드 높이에 영향을 주지 않도록 차단
    <div className={`bg-innerground-white relative h-full w-full overflow-hidden rounded-lg border-3 ${currentLevelColors.border}`}>
      {/* absolute inset-0: 외부 div를 꽉 채우며 flex-col 레이아웃 */}
      <div className="absolute inset-0 flex flex-col gap-2 p-4 text-xs">
        {/* 우상단 레벨 뱃지 */}
        <div className="absolute top-0 right-0 overflow-hidden">
          <div className={`${currentLevelColors.bg} text-innerground-white rounded-bl-lg px-2 text-center font-semibold`}>
            {!tag.excludedYn ? tag.accountStat.currentLevel : 'EXCLUDED'}
          </div>
        </div>

        {/* 헤더 - shrink-0으로 고정 높이 유지 */}
        <div className="shrink-0 text-sm font-semibold">{TAG_INFO[tag.tagCode]?.kr ?? tag.tagDisplayName} 풀이 문제</div>

        {/* 문제 목록 - flex-1 + min-h-0으로 남은 공간을 채우며 스크롤 */}
        <div className="hide-scrollbar min-h-0 flex-1 overflow-y-auto">
          <div className="flex flex-col gap-1">
            {isPending && <div className="text-muted-foreground py-4 text-center">불러오는 중...</div>}

            {isError && !isPending && <div className="text-destructive py-4 text-center">문제 정보를 불러올 수 없습니다.</div>}

            {tagDetail && !isPending && (
              <>
                <div className="text-muted-foreground mb-1">총 {tagDetail.totalProblemCount}개</div>
                {sortedProblems.map((problem) => (
                  <div key={problem.problemId} className="flex items-center justify-between gap-2 rounded border px-2 py-1.5">
                    <div className="flex min-w-0 items-center gap-2">
                      <Image
                        src={`/tiers/tier_${problem.problemTierLevel}.svg`}
                        alt={TIER_INFO[problem.problemTierLevel as keyof typeof TIER_INFO]?.short ?? problem.problemTierName}
                        width={14}
                        height={14}
                        className="shrink-0"
                      />
                      <span className="truncate">
                        {problem.problemId}. {problem.problemTitle}
                      </span>
                    </div>
                    <span className={`shrink-0 ${problem.solvedDate ? 'text-advanced-bg font-semibold' : 'text-muted-foreground'}`}>
                      {problem.solvedDate
                        ? getDaysAgo(problem.solvedDate) === 0
                          ? '오늘 풀이'
                          : `${getDaysAgo(problem.solvedDate)}일 전`
                        : '가입 전 풀이'}
                    </span>
                  </div>
                ))}
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
