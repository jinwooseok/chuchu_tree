'use client';

import { useEffect, useMemo } from 'react';
import { useInView } from 'react-intersection-observer';
import Image from 'next/image';
import { useGetStudyRecommendHistory } from '@/entities/study';
import { TAG_INFO } from '@/shared/constants/tagSystem';

function formatTimestamp(createdAt: string): string {
  const date = new Date(createdAt);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 1) return '방금 전';
  if (diffMins < 60) return `${diffMins}분 전`;
  if (diffHours < 24) return `${diffHours}시간 전`;
  if (diffDays < 7) return `${diffDays}일 전`;

  const month = date.getMonth() + 1;
  const day = date.getDate();
  const hours = date.getHours();
  const minutes = date.getMinutes();
  return `${month}월 ${day}일 ${hours}:${minutes.toString().padStart(2, '0')}`;
}

export function StudyRecommendHistorySection({ studyId }: { studyId: number }) {
  const { data, fetchNextPage, hasNextPage, isFetchingNextPage, isLoading } = useGetStudyRecommendHistory(studyId);

  const { ref: bottomRef, inView } = useInView({ threshold: 0 });

  useEffect(() => {
    if (inView && hasNextPage && !isFetchingNextPage) {
      fetchNextPage();
    }
  }, [inView, hasNextPage, isFetchingNextPage, fetchNextPage]);

  const historyItems = useMemo(() => data?.pages.flatMap((page) => page.items) ?? [], [data]);

  if (isLoading) {
    return (
      <div className="w-full py-4 text-center">
        <p className="text-muted-foreground text-sm">불러오는 중...</p>
      </div>
    );
  }

  if (historyItems.length === 0) {
    return (
      <div className="w-full py-4 text-center">
        <p className="text-muted-foreground text-sm">추천 기록이 없습니다.</p>
      </div>
    );
  }

  return (
    <div className="w-full space-y-3">
      <h3 className="text-sm font-semibold">추천 기록</h3>
      {historyItems.map((historyItem) => (
        <div key={historyItem.recommendationHistoryId} className="bg-innerground-hovergray/30 rounded-lg">
          <div className="flex items-center gap-3 rounded-t-lg p-3">
            <span className="text-sm font-medium">{formatTimestamp(historyItem.createdAt)}</span>
            <span className="text-muted-foreground text-xs">{historyItem.recommendedProblems.length}개 문제</span>
          </div>

          <div className="space-y-1.5 px-3 pb-3">
            {historyItem.recommendedProblems.map((problem) => {
              const firstTag = problem.tags[0];
              const tagName = firstTag ? (TAG_INFO[firstTag.tagCode as keyof typeof TAG_INFO]?.kr ?? firstTag.tagDisplayName) : null;

              return (
                <div
                  key={problem.problemId}
                  className="bg-innerground-hovergray/50 hover:bg-innerground-darkgray/70 flex cursor-pointer items-center justify-between rounded-lg px-3 py-2 text-xs transition-colors"
                  onClick={() => window.open(`https://www.acmicpc.net/problem/${problem.problemId}`, '_blank')}
                >
                  <div className="flex items-center gap-2">
                    <Image src={`/tiers/tier_${problem.problemTierLevel}.svg`} alt={`Tier ${problem.problemTierLevel}`} width={16} height={16} />
                    <span className="text-muted-foreground">#{problem.problemId}</span>
                    <span className="font-medium">{problem.problemTitle}</span>
                  </div>
                  <div className="flex flex-col items-end gap-0.5">
                    {tagName && <span className="text-muted-foreground line-clamp-1">{tagName}</span>}
                    {problem.recommandReasons.length > 0 && (
                      <span className="text-muted-foreground line-clamp-1">{problem.recommandReasons[0].reason}</span>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      ))}

      {/* 무한스크롤 트리거 */}
      <div ref={bottomRef} className="py-2 text-center">
        {isFetchingNextPage && <p className="text-muted-foreground text-xs">불러오는 중...</p>}
        {!hasNextPage && <p className="text-muted-foreground text-xs">더 이상 기록이 없습니다.</p>}
      </div>
    </div>
  );
}
