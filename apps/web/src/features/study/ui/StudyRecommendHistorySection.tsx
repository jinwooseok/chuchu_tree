'use client';

import { useEffect, useMemo, useState } from 'react';
import { useInView } from 'react-intersection-observer';
import { TierSvg } from '@/shared/ui';
import { useGetStudyRecommendHistory, useResetStudyRecommendHistory, StudyDetail, StudyRecommendHistoryProblem, useAssignProblemAll, useAssignProblemIndividual, useStudyProblems } from '@/entities/study';
import { TAG_INFO } from '@/shared/constants/tagSystem';
import { UserAvatar } from '@/components/custom/UserAvatar';
import { AppTooltip } from '@/components/custom/tooltip/AppTooltip';
import { Button } from '@/components/ui/button';
import { RotateCcw, EyeOff, CheckCircle } from 'lucide-react';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { useStudyRecommendStore } from '@/lib/store/studyRecommend';
import { useStudyCalendarStore } from '@/lib/store/studyCalendar';
import { formatDateString } from '@/lib/utils/date';
import { toast } from '@/lib/utils/toast';

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
  showAlgorithm: boolean;
}

function ParamsBadges({ params, requesterUserAccountId, members, showAlgorithm }: ParamsBadgesProps) {
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

  // 태그 필터 — 알고리즘 표시항목 켜져있을 때만 표시
  if (showAlgorithm && params.tagFilterCodes.length > 0) {
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

function HistoryProblemCard({
  problem,
  showFilters,
  studyDetail,
  studyId,
  assignedProblemIds,
}: {
  problem: StudyRecommendHistoryProblem;
  showFilters: { problemNumber: boolean; problemTier: boolean; recommendReason: boolean; algorithm: boolean };
  studyDetail: StudyDetail;
  studyId: number;
  assignedProblemIds: Set<number>;
}) {
  const [assignPopoverOpen, setAssignPopoverOpen] = useState(false);
  const [selectedMemberIds, setSelectedMemberIds] = useState<number[]>([]);

  const { selectedDate } = useStudyCalendarStore();
  const isAlreadyAssigned = assignedProblemIds.has(problem.problemId);

  const { mutate: assignAll, isPending: isAssigningAll } = useAssignProblemAll(studyId, {
    onSuccess: () => {
      toast.success('전원에게 문제가 할당되었습니다.');
      setAssignPopoverOpen(false);
    },
    onError: () => toast.error('문제 할당에 실패했습니다.'),
  });

  const { mutate: assignIndividual, isPending: isAssigningIndividual } = useAssignProblemIndividual(studyId, {
    onSuccess: () => {
      toast.success('문제가 할당되었습니다.');
      setAssignPopoverOpen(false);
      setSelectedMemberIds([]);
    },
    onError: () => toast.error('문제 할당에 실패했습니다.'),
  });

  const handleAssignAll = () => {
    if (!selectedDate) {
      toast.error('날짜를 먼저 선택해주세요.');
      return;
    }
    assignAll({ problemId: problem.problemId, targetDate: formatDateString(selectedDate) });
  };

  const handleAssignIndividual = () => {
    if (!selectedDate) {
      toast.error('날짜를 먼저 선택해주세요.');
      return;
    }
    if (selectedMemberIds.length === 0) return;
    assignIndividual({
      problemId: problem.problemId,
      assignments: selectedMemberIds.map((id) => ({ userAccountId: id, targetDate: formatDateString(selectedDate) })),
    });
  };

  const toggleMember = (userAccountId: number) => {
    setSelectedMemberIds((prev) => (prev.includes(userAccountId) ? prev.filter((id) => id !== userAccountId) : [...prev, userAccountId]));
  };

  const firstTag = problem.tags[0];
  const tagName = firstTag ? (TAG_INFO[firstTag.tagCode as keyof typeof TAG_INFO]?.kr ?? firstTag.tagDisplayName) : null;
  const isPending = isAssigningAll || isAssigningIndividual;

  return (
    <div className="flex">
      {/* 할당 버튼 */}
      {isAlreadyAssigned ? (
        <Button
          className="bg-destructive text-destructive-foreground hover:bg-destructive/90 h-auto min-h-9 w-8 cursor-pointer items-center justify-center rounded-l-lg rounded-r-none text-xs"
          onClick={(e) => {
            e.stopPropagation();
            toast.info('이미 등록된 문제입니다.');
          }}
        >
          <CheckCircle className="h-5 w-5" />
        </Button>
      ) : (
        <Popover open={assignPopoverOpen} onOpenChange={setAssignPopoverOpen}>
          <PopoverTrigger asChild>
            <Button
              className="bg-innerground-darkgray text-muted-foreground hover:bg-primary hover:text-primary-foreground h-auto min-h-9 w-8 cursor-pointer items-center justify-center rounded-l-lg rounded-r-none text-xs"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex flex-col leading-tight">
                <span>문제</span>
                <span>할당</span>
              </div>
            </Button>
          </PopoverTrigger>
          <PopoverContent side="left" className="w-44 p-2" onClick={(e) => e.stopPropagation()}>
            <p className="text-muted-foreground mb-2 text-xs font-medium">문제 할당</p>
            <Button size="sm" className="mb-2 w-full text-xs" onClick={handleAssignAll} disabled={isPending}>
              전원에게 할당
            </Button>
            <div className="mb-2 border-t pt-2">
              <p className="text-muted-foreground mb-1.5 text-xs">특정 멤버 선택</p>
              <div className="flex flex-wrap gap-1">
                {studyDetail.members.map((member) => (
                  <button
                    key={member.userAccountId}
                    onClick={() => toggleMember(member.userAccountId)}
                    className={`rounded-full transition-all ${selectedMemberIds.includes(member.userAccountId) ? 'ring-primary ring-2 ring-offset-1' : 'opacity-50 hover:opacity-100'}`}
                  >
                    <UserAvatar profileImageUrl={member.profileImageUrl} bjAccountId={member.bjAccountId} userCode={member.userCode} size={24} />
                  </button>
                ))}
              </div>
            </div>
            <Button size="sm" variant="outline" className="w-full text-xs" onClick={handleAssignIndividual} disabled={isPending || selectedMemberIds.length === 0}>
              선택 멤버에게 할당 {selectedMemberIds.length > 0 ? `(${selectedMemberIds.length}명)` : ''}
            </Button>
          </PopoverContent>
        </Popover>
      )}

      {/* 문제 정보 */}
      <div
        className="bg-innerground-hovergray/50 hover:bg-innerground-darkgray/70 flex flex-1 cursor-pointer items-center justify-between rounded-l-none rounded-r-lg px-3 py-2 text-xs transition-colors"
        onClick={() => window.open(`https://www.acmicpc.net/problem/${problem.problemId}`, '_blank')}
      >
        <div className="flex items-center gap-2">
          {showFilters.problemTier && <TierSvg tier={problem.problemTierLevel} size={16} />}
          {showFilters.problemNumber && <span className="text-muted-foreground">#{problem.problemId}</span>}
          <span className="font-medium">{problem.problemTitle}</span>
        </div>
        <div className="flex flex-col items-end gap-0.5">
          {showFilters.algorithm && tagName && <span className="text-muted-foreground line-clamp-1">{tagName}</span>}
          {showFilters.recommendReason && problem.recommandReasons.length > 0 && (
            <span className="text-muted-foreground line-clamp-1">
              {showFilters.algorithm
                ? problem.recommandReasons[0].reason
                : problem.recommandReasons[0].reason
                    .replace(/'[^']+'/g, '')
                    .replace(/\s+/g, ' ')
                    .trim()}
            </span>
          )}
        </div>
      </div>
    </div>
  );
}

export function StudyRecommendHistorySection({ studyId, studyDetail }: { studyId: number; studyDetail: StudyDetail }) {
  const [selectedMemberId, setSelectedMemberId] = useState<number | null>(null);
  const { showFilters, toggleFilter } = useStudyRecommendStore();
  const { selectedDate, bigCalendarDate } = useStudyCalendarStore();

  const year = bigCalendarDate?.getFullYear() ?? new Date().getFullYear();
  const month = (bigCalendarDate?.getMonth() ?? new Date().getMonth()) + 1;
  const { data: calendarData } = useStudyProblems(studyId, year, month);

  const assignedProblemIds = useMemo(() => {
    if (!selectedDate || !calendarData) return new Set<number>();
    const dateStr = formatDateString(selectedDate);
    const dayData = calendarData.monthlyData.find((d) => d.targetDate === dateStr);
    return new Set<number>(dayData?.problems.map((p) => p.problemId) ?? []);
  }, [selectedDate, calendarData]);

  const { data, fetchNextPage, hasNextPage, isFetchingNextPage, isLoading } = useGetStudyRecommendHistory(studyId, selectedMemberId);
  const { mutate: resetHistory } = useResetStudyRecommendHistory(studyId);

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
      <div className="flex items-center gap-4">
        <h3 className="text-xl font-semibold">추천 기록</h3>
        {/* 추천기록 초기화 버튼 */}
        <AppTooltip content="추천기록 초기화" side="top">
          <Button onClick={() => resetHistory()} variant="outline" size="icon" aria-label="추천기록 초기화" className="text-muted-foreground hover:text-foreground shrink-0 cursor-pointer">
            <RotateCcw className="h-4 w-4" />
          </Button>
        </AppTooltip>
        {/* 표시항목 */}
        <Popover>
          <AppTooltip content="표시 항목" side="top">
            <PopoverTrigger asChild>
              <button aria-label="표시 항목창 열기" className="relative cursor-pointer">
                <EyeOff className="text-muted-foreground h-4 w-4" />
              </button>
            </PopoverTrigger>
          </AppTooltip>
          <PopoverContent className="w-36 p-2">
            <div className="text-muted-foreground mb-2 text-xs font-semibold">표시 항목</div>
            <div className="space-y-2">
              {(
                [
                  { key: 'problemNumber', label: '문제번호' },
                  { key: 'problemTier', label: '문제티어' },
                  { key: 'recommendReason', label: '추천이유' },
                  { key: 'algorithm', label: '알고리즘' },
                ] as const
              ).map((filter) => (
                <label key={filter.key} className="hover:bg-background/60 flex cursor-pointer items-center gap-2 rounded p-1">
                  <input
                    type="checkbox"
                    checked={showFilters[filter.key]}
                    onChange={() => toggleFilter(filter.key)}
                    className="checked:bg-primary checked:border-primary border-muted-foreground h-4 w-4 cursor-pointer appearance-none rounded border-2"
                  />
                  <span className="text-xs">{filter.label}</span>
                </label>
              ))}
            </div>
          </PopoverContent>
        </Popover>
        <div className="ml-4 flex items-center gap-1.5">
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
                <ParamsBadges params={historyItem.params} requesterUserAccountId={historyItem.requesterUserAccountId} members={studyDetail.members} showAlgorithm={showFilters.algorithm} />
              </div>

              {/* 문제 목록 */}
              <div className="space-y-1.5 px-3 pb-3">
                {historyItem.recommendedProblems.map((problem) => (
                  <HistoryProblemCard
                    key={problem.problemId}
                    problem={problem}
                    showFilters={showFilters}
                    studyDetail={studyDetail}
                    studyId={studyId}
                    assignedProblemIds={assignedProblemIds}
                  />
                ))}
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
