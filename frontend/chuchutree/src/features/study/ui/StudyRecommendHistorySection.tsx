'use client';

import { useEffect, useMemo, useState } from 'react';
import { useInView } from 'react-intersection-observer';
import Image from 'next/image';
import { useGetStudyRecommendHistory } from '@/entities/study';
import { StudyDetail } from '@/entities/study';
import { TAG_INFO } from '@/shared/constants/tagSystem';
import { UserAvatar } from '@/components/custom/UserAvatar';

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

const LEVEL_LABEL: Record<string, string> = {
  easy: 'Easy',
  normal: 'Normal',
  hard: 'Hard',
  extreme: 'Extreme',
};

const EXCLUSION_MODE_LABEL: Record<string, string> = {
  STRICT: '엄격한 제외',
  LENIENT: '느슨한 제외',
};

interface ParamsBadgesProps {
  params: {
    count: number;
    exclusionMode: string;
    levelFilterCodes: string[] | null;
    tagFilterCodes: string[];
    targetUserAccountId: number | null;
    recommendAllUnsolved: boolean;
  };
  requesterUserAccountId: number;
  members: StudyDetail['members'];
}

function ParamsBadges({ params, requesterUserAccountId, members }: ParamsBadgesProps) {
  // targetUserAccountId가 null이면 requesterUserAccountId 사용
  const effectiveTargetId = params.targetUserAccountId ?? requesterUserAccountId;
  const targetMember = members.find((m) => m.userAccountId === effectiveTargetId);

  const badges: React.ReactNode[] = [];

  // 추천 문제수
  badges.push(
    <span key="count" className="bg-innerground-hovergray text-muted-foreground rounded px-1.5 py-0.5">
      {params.count}개 추천
    </span>,
  );

  // 대상 멤버
  if (targetMember) {
    badges.push(
      <span key="target" className="flex items-center gap-1">
        <UserAvatar profileImageUrl={targetMember.profileImageUrl} bjAccountId={targetMember.bjAccountId} userCode={targetMember.userCode} size={16} />
        <span className="bg-innerground-hovergray text-muted-foreground rounded px-1.5 py-0.5">{targetMember.bjAccountId}</span>
      </span>,
    );
  }

  // 미풀이 전체 기반
  if (params.recommendAllUnsolved) {
    badges.push(
      <span key="unsolved" className="bg-primary/10 text-primary rounded px-1.5 py-0.5">
        미풀이 전체 기반
      </span>,
    );
  }

  // 레벨 필터 (null이면 Normal 표시)
  const levelLabel = !params.levelFilterCodes || params.levelFilterCodes.length === 0 ? 'Normal' : params.levelFilterCodes.map((l) => LEVEL_LABEL[l] ?? l).join(', ');
  badges.push(
    <span key="level" className="bg-innerground-hovergray text-muted-foreground rounded px-1.5 py-0.5">
      {levelLabel}
    </span>,
  );

  // 태그 필터 — 한글 태그명 표시
  if (params.tagFilterCodes.length > 0) {
    const tagNames = params.tagFilterCodes.map((code) => TAG_INFO[code as keyof typeof TAG_INFO]?.kr ?? code).join(', ');
    badges.push(
      <span key="tags" className="bg-innerground-hovergray text-muted-foreground rounded px-1.5 py-0.5">
        {tagNames}
      </span>,
    );
  }

  // 제외 모드 (항상 표시)
  if (params.exclusionMode) {
    badges.push(
      <span key="exclusion" className="bg-innerground-hovergray text-muted-foreground rounded px-1.5 py-0.5">
        {EXCLUSION_MODE_LABEL[params.exclusionMode] ?? params.exclusionMode}
      </span>,
    );
  }

  return <div className="flex flex-wrap items-center gap-1 text-xs">{badges}</div>;
}

export function StudyRecommendHistorySection({ studyId, studyDetail }: { studyId: number; studyDetail: StudyDetail }) {
  const [selectedMemberId, setSelectedMemberId] = useState<number | null>(null);

  const { data, fetchNextPage, hasNextPage, isFetchingNextPage, isLoading } = useGetStudyRecommendHistory(studyId, selectedMemberId);

  const { ref: bottomRef, inView } = useInView({ threshold: 0 });

  useEffect(() => {
    if (inView && hasNextPage && !isFetchingNextPage) {
      fetchNextPage();
    }
  }, [inView, hasNextPage, isFetchingNextPage, fetchNextPage]);

  const historyItems = useMemo(() => data?.pages.flatMap((page) => page.items) ?? [], [data]);

  const handleMemberClick = (userAccountId: number) => {
    setSelectedMemberId((prev) => (prev === userAccountId ? null : userAccountId));
  };

  return (
    <div className="relative w-full space-y-3">
      {/* 헤더: 제목 + 멤버 필터 */}
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">추천 기록</h3>
        <div className="flex items-center gap-1.5">
          <span className="text-muted-foreground text-xs">멤버 필터</span>

          {/* All 버튼 */}
          <button
            onClick={() => setSelectedMemberId(null)}
            className={`rounded-full border px-2 py-0.5 text-xs transition-all ${
              selectedMemberId === null ? 'border-primary text-primary font-semibold' : 'text-muted-foreground border-transparent opacity-50 hover:opacity-100'
            }`}
          >
            All
          </button>

          {/* 멤버 아바타 */}
          {studyDetail.members.map((member) => (
            <button
              key={member.userAccountId}
              onClick={() => handleMemberClick(member.userAccountId)}
              className={`rounded-full transition-all ${selectedMemberId === member.userAccountId ? 'ring-primary ring-2 ring-offset-1' : 'opacity-50 hover:opacity-100'}`}
            >
              <UserAvatar profileImageUrl={member.profileImageUrl} bjAccountId={member.bjAccountId} userCode={member.userCode} size={26} />
            </button>
          ))}
        </div>
      </div>

      {isLoading ? (
        <div className="w-full py-4 text-center">
          <p className="text-muted-foreground text-sm">불러오는 중...</p>
        </div>
      ) : historyItems.length === 0 ? (
        <div className="w-full py-4 text-center">
          <p className="text-muted-foreground text-sm">추천 기록이 없습니다.</p>
        </div>
      ) : (
        <>
          {historyItems.map((historyItem) => (
            <div key={historyItem.recommendationHistoryId} className="bg-innerground-hovergray/30 rounded-lg">
              {/* 히스토리 헤더: 시간 + 파라미터 배지 */}
              <div className="flex flex-col gap-1.5 rounded-t-lg p-3">
                <div className="flex items-center gap-3">
                  <span className="text-sm font-medium">{formatTimestamp(historyItem.createdAt)}</span>
                  <span className="text-muted-foreground text-xs">{historyItem.recommendedProblems.length}개 문제</span>
                </div>
                <ParamsBadges params={historyItem.params} requesterUserAccountId={historyItem.requesterUserAccountId} members={studyDetail.members} />
              </div>

              {/* 문제 목록 */}
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
                        {problem.recommandReasons.length > 0 && <span className="text-muted-foreground line-clamp-1">{problem.recommandReasons[0].reason}</span>}
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
        </>
      )}

    </div>
  );
}
