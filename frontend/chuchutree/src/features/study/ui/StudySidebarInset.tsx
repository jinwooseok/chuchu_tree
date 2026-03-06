'use client';

import { useState, useEffect, useMemo } from 'react';
import Image from 'next/image';
import { X, Search, EyeOff } from 'lucide-react';
import { useStudyCalendarStore } from '@/lib/store/studyCalendar';
import { useStudySidebarStore } from '@/lib/store/studySidebar';
import { TAG_INFO } from '@/shared/constants/tagSystem';
import { useSearchProblems, WillSolveProblems } from '@/entities/calendar';
import { StudyCalendar, StudyProblem, StudyDetail, useAssignProblemAll, useAssignProblemIndividual, useDeleteStudyProblem } from '@/entities/study';
import { formatDateString } from '@/lib/utils/date';
import { toast } from '@/lib/utils/toast';
import { getStudyProblemStatus } from '../lib/utils';
import { AppTooltip } from '@/components/custom/tooltip/AppTooltip';

type SidebarShowFilters = { algorithm: boolean; problemTier: boolean; problemNumber: boolean };

// ── 할당 문제 카드 ────────────────────────────────────────────────

function StudyProblemCard({ problem, onDelete, showFilters }: { problem: StudyProblem; onDelete: () => void; showFilters: SidebarShowFilters }) {
  const status = getStudyProblemStatus(problem);
  const isSolved = status === 'solved';
  const firstTag = problem.tags[0];
  const lastTag = problem.tags.length > 0 ? problem.tags[problem.tags.length - 1] : null;
  const tagInfo = TAG_INFO[problem.representativeTag?.tagCode || lastTag?.tagCode || firstTag?.tagCode];
  const tagDisplayName = tagInfo ? tagInfo.kr : problem.representativeTag?.tagDisplayName || lastTag?.tagDisplayName;

  return (
    <div onClick={() => window.open(`https://www.acmicpc.net/problem/${problem.problemId}`, '_blank')} className="bg-background flex cursor-pointer flex-col gap-2 rounded-md px-2 py-2 text-xs">
      {/* 문제 기본정보 + 제목 + 삭제버튼 */}
      <div className="relative flex items-center">
        {/* 전원풀이 완료 뱃지 */}
        <span className={`mr-2 shrink-0 rounded px-1.5 py-0.5 text-[10px] font-medium ${isSolved ? 'bg-primary/20 text-primary' : 'bg-innerground-darkgray text-only-gray'}`}>
          {isSolved ? '완료' : '진행중'}
        </span>

        {/* 문제 기본정보 */}
        {(showFilters.algorithm || showFilters.problemTier || showFilters.problemNumber) && (
          <div className="mr-2 flex shrink-0 flex-col gap-1 text-center">
            {showFilters.algorithm && lastTag && (
              <div className={`rounded px-2 py-0.5 ${!isSolved ? 'bg-innerground-darkgray' : tagInfo ? tagInfo.bgColor : 'bg-logo'}`}>
                <span className="line-clamp-1">{tagDisplayName}</span>
              </div>
            )}
            {(showFilters.problemTier || showFilters.problemNumber) && (
              <div className="flex items-center gap-1">
                {showFilters.problemTier && <Image src={`/tiers/tier_${problem.problemTierLevel}.svg`} alt={`Tier ${problem.problemTierLevel}`} width={12} height={12} />}
                {showFilters.problemNumber && <span>{problem.problemId}</span>}
              </div>
            )}
          </div>
        )}

        {/* 문제 제목 */}
        <div className="line-clamp-2 flex-1 pr-4 text-end">{problem.problemTitle}</div>

        {/* 삭제 버튼 */}
        <AppTooltip content="문제 할당 삭제" side="left">
          <button
            onClick={(e) => {
              e.stopPropagation();
              onDelete();
            }}
            className="text-muted-foreground hover:text-destructive absolute top-0 right-0 shrink-0 rounded p-1 transition-colors"
            aria-label="문제 할당 삭제"
          >
            <X className="h-4 w-4" />
          </button>
        </AppTooltip>
      </div>

      {/* 풀이 현황 */}
      {problem.solveInfo.length > 0 && (
        <div className="flex flex-col gap-1 border-t pt-1" onClick={(e) => e.stopPropagation()}>
          <span className="text-muted-foreground text-[10px]">풀이 현황</span>
          {problem.solveInfo.map((info) => (
            <div key={info.userAccountId} className="flex items-center gap-1.5">
              <span className={`text-[10px] ${info.solved ? 'text-primary' : 'text-muted-foreground'}`}>{info.solved ? '✓' : '✗'}</span>
              <span className="text-[10px]">
                {info.bjAccountId}#{info.userCode}
              </span>
              {info.solved && info.solveDate && <span className="text-muted-foreground text-[10px]">({info.solveDate})</span>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// ── 검색 결과 카드 ────────────────────────────────────────────────

function SearchResultCard({ problem, onClick, showFilters }: { problem: WillSolveProblems; onClick: () => void; showFilters: SidebarShowFilters }) {
  const firstTag = problem.tags[0];
  const lastTag = problem.tags.length > 0 ? problem.tags[problem.tags.length - 1] : null;
  const tagInfo = TAG_INFO[problem.representativeTag?.tagCode || lastTag?.tagCode || firstTag?.tagCode];

  return (
    <button onClick={onClick} className="bg-background hover:bg-accent flex w-full items-center gap-2 rounded-md p-2 text-left text-xs transition-colors">
      {(showFilters.algorithm || showFilters.problemTier || showFilters.problemNumber) && (
        <div className="flex shrink-0 flex-col gap-1 text-center">
          {showFilters.algorithm && lastTag && <div className={`rounded px-2 py-0.5 ${tagInfo ? tagInfo.bgColor : 'bg-only-gray'}`}>{lastTag.tagDisplayName}</div>}
          {showFilters.algorithm && !lastTag && <div className="bg-only-gray rounded px-2 py-0.5">Undefined</div>}
          {(showFilters.problemTier || showFilters.problemNumber) && (
            <div className="flex items-center gap-1">
              {showFilters.problemTier && <Image src={`/tiers/tier_${problem.problemTierLevel}.svg`} alt={`Tier ${problem.problemTierLevel}`} width={12} height={12} />}
              {showFilters.problemNumber && <span>{problem.problemId}</span>}
            </div>
          )}
        </div>
      )}
      <div className="line-clamp-2 flex-1 text-end">{problem.problemTitle}</div>
    </button>
  );
}

// ── 메인 컴포넌트 ─────────────────────────────────────────────────

type AssignStep = 'search' | 'selectMode' | 'selectMembers';

export function StudySidebarInset({ studyCalendarData, studyDetail, studyId }: { studyCalendarData?: StudyCalendar; studyDetail?: StudyDetail; studyId: number }) {
  const { selectedDate } = useStudyCalendarStore();
  const { showFilters, toggleFilter, resetFilters } = useStudySidebarStore();

  const [showFilterSection, setShowFilterSection] = useState(false);
  const [showAssignUI, setShowAssignUI] = useState(false);
  const [assignStep, setAssignStep] = useState<AssignStep>('search');
  const [searchKeyword, setSearchKeyword] = useState('');
  const [debouncedKeyword, setDebouncedKeyword] = useState('');
  const [selectedProblem, setSelectedProblem] = useState<WillSolveProblems | null>(null);
  const [selectedMemberIds, setSelectedMemberIds] = useState<number[]>([]);

  // Debounce (400ms)
  useEffect(() => {
    const timer = setTimeout(() => setDebouncedKeyword(searchKeyword), 400);
    return () => clearTimeout(timer);
  }, [searchKeyword]);

  const { data: searchResults, isLoading: isSearching } = useSearchProblems(debouncedKeyword);

  const assignProblemAll = useAssignProblemAll(studyId, {
    onSuccess: () => {
      toast.success('전원에게 문제가 할당되었습니다.');
      resetAssignUI();
    },
    onError: () => toast.error('문제 할당에 실패했습니다.'),
  });

  const assignProblemIndividual = useAssignProblemIndividual(studyId, {
    onSuccess: () => {
      toast.success('문제가 할당되었습니다.');
      resetAssignUI();
    },
    onError: () => toast.error('문제 할당에 실패했습니다.'),
  });

  const deleteStudyProblem = useDeleteStudyProblem(studyId, {
    onSuccess: () => toast.success('문제 할당이 삭제되었습니다.'),
    onError: () => toast.error('문제 할당 삭제에 실패했습니다.'),
  });

  // selectedDate 기준 할당 문제 목록
  const assignedProblems = useMemo(() => {
    if (!studyCalendarData || !selectedDate) return [];
    const dateString = formatDateString(selectedDate);
    const dayData = studyCalendarData.monthlyData.find((d) => d.targetDate === dateString);
    return dayData?.problems || [];
  }, [studyCalendarData, selectedDate]);

  const resetAssignUI = () => {
    setShowAssignUI(false);
    setAssignStep('search');
    setSearchKeyword('');
    setSelectedProblem(null);
    setSelectedMemberIds([]);
  };

  const handleProblemSelect = (problem: WillSolveProblems) => {
    setSelectedProblem(problem);
    setAssignStep('selectMode');
  };

  const handleAssignAll = () => {
    if (!selectedProblem || !selectedDate) return;
    assignProblemAll.mutate({
      problemId: selectedProblem.problemId,
      targetDate: formatDateString(selectedDate),
    });
  };

  const handleAssignIndividual = () => {
    if (!selectedProblem || !selectedDate || selectedMemberIds.length === 0) return;
    assignProblemIndividual.mutate({
      problemId: selectedProblem.problemId,
      assignments: selectedMemberIds.map((id) => ({
        userAccountId: id,
        targetDate: formatDateString(selectedDate),
      })),
    });
  };

  const toggleMember = (userAccountId: number) => {
    setSelectedMemberIds((prev) => (prev.includes(userAccountId) ? prev.filter((id) => id !== userAccountId) : [...prev, userAccountId]));
  };

  const allSearchResults = searchResults ? [...searchResults.problems.idBase, ...searchResults.problems.titleBase] : [];
  const uniqueSearchResults = Array.from(new Map(allSearchResults.map((p) => [p.problemId, p])).values());

  const sidebarFilters = [
    { key: 'problemNumber' as const, label: '문제번호' },
    { key: 'problemTier' as const, label: '문제티어' },
    { key: 'algorithm' as const, label: '알고리즘' },
  ];
  const hasFilterChanges = !showFilters.algorithm || !showFilters.problemTier || !showFilters.problemNumber;

  return (
    <div className="flex flex-col gap-8">
      {/* 표시항목 */}
      <div className="flex flex-col gap-2">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-semibold">표시항목</h3>
          <button aria-label="표시항목 설정 열기" onClick={() => setShowFilterSection((prev) => !prev)} className="text-muted-foreground hover:text-foreground relative cursor-pointer">
            <EyeOff className="h-4 w-4" />
            {hasFilterChanges && <div className="bg-primary/80 absolute top-0 -right-0.5 h-2 w-2 rounded-full" />}
          </button>
        </div>
        {showFilterSection && (
          <div className="space-y-2">
            {sidebarFilters.map((filter) => (
              <label key={filter.key} aria-label={filter.label} className="hover:bg-background/60 flex cursor-pointer items-center gap-2 rounded p-1">
                <input
                  type="checkbox"
                  checked={showFilters[filter.key]}
                  onChange={() => toggleFilter(filter.key)}
                  className="checked:bg-primary checked:border-primary border-muted-foreground h-4 w-4 cursor-pointer appearance-none rounded border-2"
                />
                <span className="text-xs">{filter.label}</span>
              </label>
            ))}
            <div className="flex justify-end">
              <button onClick={resetFilters} aria-label="표시항목 초기화" className="text-muted-foreground hover:text-foreground text-xs underline">
                초기화
              </button>
            </div>
          </div>
        )}
      </div>

      {/* 할당된 문제 목록 */}
      <div className="flex flex-col gap-2">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-semibold">할당된 문제</h3>
          <span className="text-xs text-gray-500">{assignedProblems.length}개</span>
        </div>

        {assignedProblems.length === 0 ? (
          <div className="rounded-lg border border-dashed border-gray-300 p-4 text-center text-xs text-gray-400">할당된 문제가 없습니다</div>
        ) : (
          <div className="flex flex-col gap-2">
            {assignedProblems.map((problem) => (
              <StudyProblemCard key={problem.studyProblemId} problem={problem} onDelete={() => deleteStudyProblem.mutate(problem.studyProblemId)} showFilters={showFilters} />
            ))}
          </div>
        )}

        {/* 문제 할당 UI */}
        {!showAssignUI ? (
          <button onClick={() => setShowAssignUI(true)} className="hover:bg-innerground-hovergray text-muted-foreground my-4 cursor-pointer rounded px-2 py-2 text-start text-sm">
            + 문제 할당하기
          </button>
        ) : (
          <div className="my-4 flex flex-col gap-2">
            {/* Step 1: 문제 검색 */}
            {assignStep === 'search' && (
              <>
                <div className="relative">
                  <Search className="text-muted-foreground absolute top-1/2 left-2 h-4 w-4 -translate-y-1/2" />
                  <input
                    type="text"
                    value={searchKeyword}
                    onChange={(e) => setSearchKeyword(e.target.value)}
                    onKeyDown={(e) => e.key === 'Escape' && resetAssignUI()}
                    placeholder="할당할 문제 검색..."
                    className="border-input bg-background focus:ring-ring w-full rounded border py-2 pr-3 pl-8 text-sm focus:ring-2 focus:outline-none"
                    autoFocus
                  />
                </div>
                {searchKeyword.trim().length > 0 && (
                  <div className="border-input hide-scrollbar max-h-60 overflow-y-auto rounded border">
                    {isSearching ? (
                      <div className="p-4 text-center text-xs text-gray-400">검색 중...</div>
                    ) : uniqueSearchResults.length === 0 ? (
                      <div className="p-4 text-center text-xs text-gray-400">검색 결과가 없습니다</div>
                    ) : (
                      <div className="flex flex-col gap-1 p-2">
                        {uniqueSearchResults.map((problem) => (
                          <SearchResultCard key={problem.problemId} problem={problem} onClick={() => handleProblemSelect(problem)} showFilters={showFilters} />
                        ))}
                      </div>
                    )}
                  </div>
                )}
                <button onClick={resetAssignUI} className="bg-secondary text-secondary-foreground hover:bg-secondary/80 rounded px-3 py-2 text-sm">
                  취소
                </button>
              </>
            )}

            {/* Step 2: 할당 방식 선택 */}
            {assignStep === 'selectMode' && selectedProblem && (
              <>
                <div className="bg-background rounded border p-2 text-xs">
                  <span className="text-muted-foreground">선택된 문제: </span>
                  <span className="font-medium">{selectedProblem.problemTitle}</span>
                </div>
                <p className="text-muted-foreground text-xs">할당 방식을 선택하세요</p>
                <button onClick={handleAssignAll} className="bg-primary text-primary-foreground hover:bg-primary/90 rounded px-3 py-2 text-sm">
                  전원에게 할당
                </button>
                <button onClick={() => setAssignStep('selectMembers')} className="bg-secondary text-secondary-foreground hover:bg-secondary/80 rounded px-3 py-2 text-sm">
                  특정 멤버에게 할당
                </button>
                <button onClick={() => setAssignStep('search')} className="text-muted-foreground hover:text-foreground text-xs underline">
                  ← 문제 다시 선택
                </button>
              </>
            )}

            {/* Step 3: 개인별 멤버 선택 */}
            {assignStep === 'selectMembers' && selectedProblem && (
              <>
                <div className="bg-background rounded border p-2 text-xs">
                  <span className="text-muted-foreground">선택된 문제: </span>
                  <span className="font-medium">{selectedProblem.problemTitle}</span>
                </div>
                <p className="text-muted-foreground text-xs">할당할 멤버를 선택하세요 (다중 선택 가능)</p>
                <div className="flex flex-col gap-1">
                  {(studyDetail?.members || []).map((member) => (
                    <label key={member.userAccountId} className="hover:bg-background/60 flex cursor-pointer items-center gap-2 rounded p-1">
                      <input
                        type="checkbox"
                        checked={selectedMemberIds.includes(member.userAccountId)}
                        onChange={() => toggleMember(member.userAccountId)}
                        className="checked:bg-primary checked:border-primary border-muted-foreground h-4 w-4 cursor-pointer appearance-none rounded border-2"
                      />
                      <span className="text-xs">
                        {member.bjAccountId}#{member.userCode}
                      </span>
                    </label>
                  ))}
                </div>
                <button
                  onClick={handleAssignIndividual}
                  disabled={selectedMemberIds.length === 0}
                  className="bg-primary text-primary-foreground hover:bg-primary/90 rounded px-3 py-2 text-sm disabled:opacity-50"
                >
                  할당하기 ({selectedMemberIds.length}명)
                </button>
                <button onClick={() => setAssignStep('selectMode')} className="text-muted-foreground hover:text-foreground text-xs underline">
                  ← 방식 다시 선택
                </button>
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
