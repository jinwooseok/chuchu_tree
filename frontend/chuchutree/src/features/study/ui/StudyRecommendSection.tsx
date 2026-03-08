'use client';

import Image from 'next/image';
import { Button } from '@/components/ui/button';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { AppTooltip } from '@/components/custom/tooltip/AppTooltip';
import { UserAvatar } from '@/components/custom/UserAvatar';
import { EyeOff, Search, SlidersHorizontal, EllipsisVertical, ChevronDown, CheckCircle, Check, X } from 'lucide-react';
import { useStudyRecommendStore } from '@/lib/store/studyRecommend';
import { useStudyRecommend } from '../hooks/useStudyRecommend';
import { StudyDetail, StudyMember, StudyRecommendedProblem, StudyRecommendMemberSolveInfo, useAssignProblemAll, useAssignProblemIndividual, useStudyProblems } from '@/entities/study';
import { TAG_INFO } from '@/shared/constants/tagSystem';
import { useStudyCalendarStore } from '@/lib/store/studyCalendar';
import { formatDateString } from '@/lib/utils/date';
import { toast } from '@/lib/utils/toast';
import { useState, useMemo } from 'react';

// ── 멤버 풀이 배지 ─────────────────────────────────────────────────

function MemberSolveBadge({ info, members }: { info: StudyRecommendMemberSolveInfo; members: StudyMember[] }) {
  const member = members.find((m) => m.userAccountId === info.userAccountId);
  return <UserAvatar profileImageUrl={member?.profileImageUrl ?? null} bjAccountId={info.bjAccountId} userCode={member?.userCode} size={24} />;
}

// ── 문제 카드 ──────────────────────────────────────────────────────

function StudyRecommendProblemCard({
  problem,
  showFilters,
  totalCount,
  studyDetail,
  studyId,
  assignedProblemIds,
}: {
  problem: StudyRecommendedProblem;
  showFilters: { problemNumber: boolean; problemTier: boolean; recommendReason: boolean; algorithm: boolean };
  totalCount: number;
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
    <div className={`mr-2 flex ${totalCount <= 3 ? 'h-full' : 'h-auto'}`}>
      {/* 할당 버튼 */}
      {isAlreadyAssigned ? (
        <Button
          className={`bg-destructive text-destructive-foreground hover:bg-destructive/90 ${totalCount <= 3 ? 'h-full' : 'h-auto min-h-10'} w-8 cursor-pointer items-center justify-center rounded-l-lg rounded-r-none text-xs`}
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
              className={`bg-innerground-darkgray text-muted-foreground hover:bg-primary hover:text-primary-foreground ${totalCount <= 3 ? 'h-full' : 'h-auto min-h-10'} w-8 cursor-pointer items-center justify-center rounded-l-lg rounded-r-none text-xs`}
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
        className="bg-innerground-hovergray/50 hover:bg-innerground-darkgray/70 flex flex-1 cursor-pointer items-center justify-between rounded-l-none rounded-r-lg px-2 py-1.5 text-xs transition-colors"
        onClick={() => window.open(`https://www.acmicpc.net/problem/${problem.problemId}`, '_blank')}
      >
        <div className="flex items-center gap-2">
          {showFilters.problemTier && <Image src={`/tiers/tier_${problem.problemTierLevel}.svg`} alt={`Tier ${problem.problemTierLevel}`} width={16} height={16} />}
          {showFilters.problemNumber && <span className="text-muted-foreground">#{problem.problemId}</span>}
          <span className="line-clamp-2 font-medium">{problem.problemTitle}</span>
        </div>
        <div className="flex min-w-30 flex-col items-end gap-0.5">
          <div className="flex items-center gap-1">{showFilters.algorithm && tagName && <span className="line-clamp-1">{tagName}</span>}</div>
          {showFilters.recommendReason && problem.recommandReasons.length > 0 && <p className="text-muted-foreground line-clamp-1">{problem.recommandReasons[0].reason}</p>}
          {problem.studyMemberSolveInfo.length > 0 &&
            (() => {
              const solved = problem.studyMemberSolveInfo.filter((i) => i.solved);
              const unsolved = problem.studyMemberSolveInfo.filter((i) => !i.solved);
              return (
                <div className="flex items-end gap-2">
                  {unsolved.length > 0 && (
                    <div className="flex items-center gap-0.5 opacity-40">
                      <div>new</div>
                      {unsolved.map((info) => (
                        <MemberSolveBadge key={info.userAccountId} info={info} members={studyDetail.members} />
                      ))}
                    </div>
                  )}
                  {solved.length > 0 && (
                    <div className="flex items-center gap-0.5">
                      <Check className="text-primary h-3 w-3 shrink-0" />
                      {solved.map((info) => (
                        <MemberSolveBadge key={info.userAccountId} info={info} members={studyDetail.members} />
                      ))}
                    </div>
                  )}
                </div>
              );
            })()}
        </div>
      </div>
    </div>
  );
}

// ── 결과 패널 ──────────────────────────────────────────────────────

function StudyRecommendAnswer({ studyDetail, studyId }: { studyDetail: StudyDetail; studyId: number }) {
  const { problems, isLoading, showFilters } = useStudyRecommendStore();
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

  if (isLoading) {
    return (
      <div className="flex h-full w-full flex-col items-center justify-center gap-2 rounded-lg border-2 border-dashed p-2">
        <div className="text-muted-foreground text-sm">추천 중...</div>
      </div>
    );
  }

  if (problems.length === 0) {
    return (
      <div className="flex h-full flex-1 flex-col items-center justify-center gap-2 rounded-lg border-2 border-dashed p-2">
        <div className="text-muted-foreground text-sm">추천받기 버튼을 눌러주세요</div>
      </div>
    );
  }

  const totalSlots = 3;
  const emptySlots = problems.length < totalSlots ? totalSlots - problems.length : 0;

  return (
    <div className="h-full w-full flex-1 rounded-lg border-2 border-dashed p-2">
      <div className={`flex h-full flex-col gap-1 overflow-x-hidden ${problems.length <= 3 ? 'overflow-y-hidden' : 'overflow-y-scroll'}`}>
        {problems.map((problem) => (
          <StudyRecommendProblemCard
            key={problem.problemId}
            problem={problem}
            showFilters={showFilters}
            totalCount={problems.length}
            studyDetail={studyDetail}
            studyId={studyId}
            assignedProblemIds={assignedProblemIds}
          />
        ))}
        {Array.from({ length: emptySlots }).map((_, index) => (
          <div key={`empty-${index}`} className="mr-2 flex h-full rounded-lg">
            <div className="bg-innerground-hovergray/50 text-muted-foreground flex h-full flex-1 cursor-default items-center justify-center rounded-lg text-xs">
              필터를 조정하면 더 많은 문제를 추천받을 수 있습니다
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// ── 컨트롤 패널 ────────────────────────────────────────────────────

function StudyRecommendButton({ studyDetail, currentUserAccountId, studyId }: { studyDetail: StudyDetail; currentUserAccountId: number; studyId: number }) {
  const {
    targetMemberId,
    recommendAllUnsolved,
    selectedLevels,
    selectedTagsList,
    selectedExclusionMode,
    selectedCount,
    showFilters,
    showLevelSection,
    showTagSection,
    showFilterSection,
    showExcludedModeSection,
    setTargetMemberId,
    setRecommendAllUnsolved,
    setSelectedLevels,
    setSelectedTagsList,
    setSelectedExclusionMode,
    setSelectedCount,
    toggleFilter,
    resetFilters,
    toggleLevelSection,
    toggleTagSection,
    toggleFilterSection,
    toggleExcludedModeSection,
  } = useStudyRecommendStore();

  const [isCountPopoverOpen, setIsCountPopoverOpen] = useState(false);
  const { recommend, isPending } = useStudyRecommend(studyId);

  const effectiveTargetId = targetMemberId || currentUserAccountId;

  const toggleLevel = (level: string) => setSelectedLevels(selectedLevels.includes(level) ? selectedLevels.filter((l) => l !== level) : [...selectedLevels, level]);
  const toggleTag = (tag: string) => setSelectedTagsList(selectedTagsList.includes(tag) ? selectedTagsList.filter((t) => t !== tag) : [...selectedTagsList, tag]);

  const levels = ['easy', 'normal', 'hard', 'extreme'] as const;
  const filters = [
    { key: 'problemNumber' as const, label: '문제번호' },
    { key: 'problemTier' as const, label: '문제티어' },
    { key: 'recommendReason' as const, label: '추천이유' },
    { key: 'algorithm' as const, label: '알고리즘' },
  ];
  const initialShowFilters = { problemNumber: true, problemTier: true, recommendReason: true, algorithm: false };

  const hasTagChanges = selectedTagsList.length > 0;
  const hasFilterChanges = JSON.stringify(showFilters) !== JSON.stringify(initialShowFilters);
  const hasLevelChanges = selectedLevels.length > 0;
  const etcIsChanged = selectedExclusionMode !== 'LENIENT' || selectedCount !== 3;

  return (
    <div className="flex h-full gap-1">
      <div className="flex h-full w-50 flex-col gap-2 rounded-lg border-2 border-dashed p-2">
        {/* 헤더: 아이콘 버튼들 */}
        <div className="flex items-center justify-between pl-2 text-xs">
          <div className="text-muted-foreground cursor-default text-center text-xs font-semibold">문제 추천</div>
          <div className="flex items-center justify-center gap-2">
            <AppTooltip content="알고리즘 유형 선택" side="top">
              <div aria-label="알고리즘 유형 선택창 열기" className="relative cursor-pointer" onClick={toggleTagSection}>
                <Search className="text-muted-foreground h-4 w-4" />
                {hasTagChanges && <div className="bg-primary/80 absolute top-0 -right-0.5 h-2 w-2 rounded-full" />}
              </div>
            </AppTooltip>
            <AppTooltip content="표시 항목" side="top">
              <div aria-label="표시 항목창 열기" className="relative cursor-pointer" onClick={toggleFilterSection}>
                <EyeOff className="text-muted-foreground h-4 w-4" />
                {hasFilterChanges && <div className="bg-primary/80 absolute top-0 -right-0.5 h-2 w-2 rounded-full" />}
              </div>
            </AppTooltip>
            <AppTooltip content="난이도 선택" side="top">
              <div aria-label="난이도 선택창 열기" className="relative cursor-pointer" onClick={toggleLevelSection}>
                <SlidersHorizontal className="text-muted-foreground h-4 w-4" />
                {hasLevelChanges && <div className="bg-primary/80 absolute top-0 -right-0.5 h-2 w-2 rounded-full" />}
              </div>
            </AppTooltip>
            <AppTooltip content="기타 설정" side="top">
              <div aria-label="기타 설정창 열기" className="relative cursor-pointer" onClick={toggleExcludedModeSection}>
                <EllipsisVertical className="text-muted-foreground h-4 w-4" />
                {selectedExclusionMode !== 'LENIENT' && <div className="bg-primary/80 absolute top-0 -right-0.5 h-2 w-2 rounded-full" />}
              </div>
            </AppTooltip>
          </div>
        </div>

        {/* 멤버 선택 */}
        <span className="text-muted-foreground mt-2 text-xs">선택한 맴버를 기준으로 추천받기</span>
        <div className="mb-2 flex flex-wrap gap-1">
          {studyDetail.members.map((member) => (
            <button
              key={member.userAccountId}
              onClick={() => setTargetMemberId(member.userAccountId)}
              className={`rounded-full transition-all ${effectiveTargetId === member.userAccountId ? 'ring-primary ring-2 ring-offset-1' : 'opacity-50 hover:opacity-100'}`}
            >
              <UserAvatar profileImageUrl={member.profileImageUrl} bjAccountId={member.bjAccountId} userCode={member.userCode} size={30} />
            </button>
          ))}
        </div>

        {/* 미풀이 전체 기반 */}
        <label className="hover:bg-background/60 flex cursor-pointer items-center gap-2 rounded px-1">
          <input
            type="checkbox"
            checked={recommendAllUnsolved}
            onChange={(e) => setRecommendAllUnsolved(e.target.checked)}
            className="checked:bg-primary checked:border-primary border-muted-foreground h-4 w-4 cursor-pointer appearance-none rounded border-2"
          />
          <span className={`text-xs ${recommendAllUnsolved ? '' : 'text-muted-foreground'}`}>모두가 처음푸는 문제 추천받기</span>
        </label>

        {/* 알고리즘 유형 멀티셀렉트 */}
        {showTagSection && (
          <Popover>
            <AppTooltip content="선택한 알고리즘 유형만 추천됩니다." side="right">
              <PopoverTrigger asChild>
                <Button aria-label="알고리즘 유형 선택" variant="outline" className="w-full cursor-pointer justify-between text-xs">
                  {selectedTagsList.length > 0 ? `${selectedTagsList.length}개 선택됨` : '알고리즘 선택'}
                  <ChevronDown className="ml-2 h-4 w-4" />
                </Button>
              </PopoverTrigger>
            </AppTooltip>
            <PopoverContent className="w-64 p-2">
              <div className="max-h-64 space-y-2 overflow-y-auto">
                {Object.entries(TAG_INFO)
                  .sort(([, a], [, b]) => a.kr.localeCompare(b.kr, 'ko'))
                  .map(([tagKey, tagInfo]) => (
                    <label key={tagKey} className="hover:bg-background/60 flex cursor-pointer items-center gap-2 rounded p-1">
                      <input
                        type="checkbox"
                        checked={selectedTagsList.includes(tagKey)}
                        onChange={() => toggleTag(tagKey)}
                        className="checked:bg-primary checked:border-primary border-muted-foreground h-4 w-4 cursor-pointer appearance-none rounded border-2"
                      />
                      <span className="text-xs">{tagInfo.kr}</span>
                    </label>
                  ))}
              </div>
              <div className="mt-2 flex justify-end border-t pt-2">
                <button onClick={() => setSelectedTagsList([])} className="text-muted-foreground hover:text-foreground text-xs underline">
                  전체 해제
                </button>
              </div>
            </PopoverContent>
          </Popover>
        )}

        {/* 추천받기 버튼 */}
        <AppTooltip content="추천 받기" side="top">
          <Button aria-label="스터디 문제 추천받기" className="flex flex-1 cursor-pointer flex-col" onClick={recommend} disabled={isPending}>
            {isPending ? '추천 중...' : '추천 받기'}
          </Button>
        </AppTooltip>
      </div>

      {/* 레벨/필터/기타 섹션 */}
      <div className={`h-full rounded-lg ${showLevelSection || showFilterSection ? 'w-26 border-2 border-dashed p-2' : showExcludedModeSection ? 'w-40 border-2 border-dashed p-2' : ''}`}>
        {showLevelSection && (
          <div>
            <div className="text-muted-foreground mb-4 cursor-default text-xs font-semibold">난이도 선택</div>
            <div className="space-y-5">
              {levels.map((level) => (
                <label key={level} className="hover:bg-background/60 flex cursor-pointer items-center gap-2 rounded">
                  <input
                    type="checkbox"
                    checked={selectedLevels.includes(level)}
                    onChange={() => toggleLevel(level)}
                    className="checked:bg-primary checked:border-primary border-muted-foreground h-4 w-4 cursor-pointer appearance-none rounded border-2"
                  />
                  <span className="text-xs capitalize">{level}</span>
                </label>
              ))}
            </div>
            {selectedLevels.length > 0 && (
              <div className="mt-4 mr-2 flex justify-end">
                <button onClick={() => setSelectedLevels([])} className="text-muted-foreground text-xs underline">
                  전체 해제
                </button>
              </div>
            )}
          </div>
        )}
        {showFilterSection && (
          <div>
            <div className="text-muted-foreground mb-4 cursor-default text-xs font-semibold">표시 항목</div>
            <div className="space-y-5">
              {filters.map((filter) => (
                <label key={filter.key} className="hover:bg-background/60 flex cursor-pointer items-center gap-2 rounded">
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
            {hasFilterChanges && (
              <div className="mt-4 mr-2 flex justify-end">
                <button onClick={resetFilters} className="text-muted-foreground hover:text-foreground text-xs underline">
                  초기화
                </button>
              </div>
            )}
          </div>
        )}
        {showExcludedModeSection && (
          <div>
            <div className="text-muted-foreground mb-2 cursor-default text-xs font-semibold">제외된 태그 설정</div>
            <div className="space-y-2">
              {(['STRICT', 'LENIENT'] as const).map((mode) => (
                <label key={mode} className="hover:bg-background/60 flex cursor-pointer items-start gap-2 rounded">
                  <input
                    type="checkbox"
                    checked={selectedExclusionMode === mode}
                    onChange={() => setSelectedExclusionMode(mode)}
                    className="checked:bg-primary checked:border-primary border-muted-foreground h-4 w-4 shrink-0 cursor-pointer appearance-none rounded border-2"
                  />
                  <div className="flex flex-col gap-1">
                    <span className="text-xs">{mode === 'STRICT' ? '엄격한 제외' : '느슨한 제외'}</span>
                    <span className="text-muted-foreground text-xs">{mode === 'STRICT' ? '제외된 유형이 절대 추천되지 않음' : '제외된 유형 때문에 추천되지는 않음'}</span>
                  </div>
                </label>
              ))}
            </div>
            <div className="mt-2 mr-2 flex items-center justify-between text-xs">
              <div className="text-muted-foreground cursor-default font-semibold">추천 문제수</div>
              <Popover open={isCountPopoverOpen} onOpenChange={setIsCountPopoverOpen}>
                <PopoverTrigger asChild>
                  <Button aria-label="문제수 선택" variant="outline" className="h-6 w-4 cursor-pointer text-xs">
                    {selectedCount}
                  </Button>
                </PopoverTrigger>
                <PopoverContent className="w-16 p-2">
                  <div className="max-h-64 space-y-2 overflow-y-auto">
                    {[1, 2, 3, 4, 5, 6].map((cnt) => (
                      <label key={cnt} className="hover:bg-background/60 flex cursor-pointer items-center gap-2 rounded p-1">
                        <input
                          type="checkbox"
                          checked={selectedCount === cnt}
                          onChange={() => {
                            setSelectedCount(cnt);
                            setIsCountPopoverOpen(false);
                          }}
                          className="checked:bg-primary checked:border-primary border-muted-foreground h-4 w-4 cursor-pointer appearance-none rounded border-2"
                        />
                        <span className="text-xs">{cnt}</span>
                      </label>
                    ))}
                  </div>
                </PopoverContent>
              </Popover>
            </div>
            {etcIsChanged && (
              <div className="mt-2 mr-2 flex justify-end">
                <button
                  onClick={() => {
                    setSelectedExclusionMode('LENIENT');
                    setSelectedCount(3);
                  }}
                  className="text-muted-foreground hover:text-foreground text-xs underline"
                >
                  초기화
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

// ── 메인 섹션 (BottomRecommend 구조) ──────────────────────────────

export function StudyRecommendSection({ studyDetail, currentUserAccountId }: { studyDetail: StudyDetail; currentUserAccountId: number }) {
  return (
    <div className="flex h-80 w-full items-center justify-between gap-2">
      <StudyRecommendButton studyDetail={studyDetail} currentUserAccountId={currentUserAccountId} studyId={studyDetail.studyId} />
      <StudyRecommendAnswer studyDetail={studyDetail} studyId={studyDetail.studyId} />
    </div>
  );
}
