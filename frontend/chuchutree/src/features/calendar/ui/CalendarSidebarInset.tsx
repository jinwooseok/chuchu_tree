'use client';

import dynamic from 'next/dynamic';
import { useCalendarStore } from '@/lib/store/calendar';
import { TAG_INFO } from '@/shared/constants/tagSystem';
import { Problem, useUpdateWillSolveProblems, useUpdateSolvedProblems, useSearchProblems, WillSolveProblems, useUpdateRepresentativeTag, Calendar } from '@/entities/calendar';
import Image from 'next/image';
import { useState, useEffect, useMemo, useId } from 'react';
import { DndContext, closestCenter, KeyboardSensor, PointerSensor, useSensor, useSensors, DragEndEvent } from '@dnd-kit/core';
import { arrayMove, SortableContext, sortableKeyboardCoordinates, useSortable, verticalListSortingStrategy } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import { GripVertical, X, Search, PencilLine, EyeOff } from 'lucide-react';
import { toast } from '@/lib/utils/toast';
import { AppTooltip } from '@/components/custom/tooltip/AppTooltip';
import { formatDateString } from '@/lib/utils/date';
import { getErrorCode, getErrorMessage } from '@/lib/utils/error';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import HelpPopover from '@/shared/ui/help-popover';
import { useCalendarSidebarStore } from '@/lib/store/calendarSidebar';

// // 클라이언트 전용 렌더링 (hydration mismatch 방지)
// const SmallCalendar = dynamic(() => import('@/features/calendar/ui/SmallCalendar'), {
//   ssr: false,
//   loading: () => (
//     <div className="flex items-center justify-center" style={{ minHeight: '300px' }}>
//       <div className="text-sm text-gray-400">Loading...</div>
//     </div>
//   ),
// });

// 드래그 가능한 문제 카드
type SidebarShowFilters = { algorithm: boolean; problemTier: boolean; problemNumber: boolean };

function DraggableProblemCard({
  problem,
  isSolved,
  onDelete,
  onUpdateRepresentativeTag,
  showFilters,
}: {
  problem: Problem;
  isSolved: boolean;
  onDelete?: () => void;
  onUpdateRepresentativeTag?: (tagCode: string) => void;
  showFilters: SidebarShowFilters;
}) {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({ id: problem.problemId });
  const [isTagOpen, setIsTagOpen] = useState<boolean>(false);
  const handleRepresentativeTag = (tagCode: string) => {
    if (onUpdateRepresentativeTag) {
      onUpdateRepresentativeTag(tagCode);
    }
    setIsTagOpen(false);
  };

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
  };

  const firstTag = problem.tags[0];
  const lastTag = problem.tags.length > 0 ? problem.tags[problem.tags.length - 1] : null;
  const tagInfo = TAG_INFO[problem.representativeTag?.tagCode || lastTag?.tagCode || firstTag?.tagCode];
  const tagDisplayName = tagInfo ? tagInfo.kr : problem.representativeTag?.tagDisplayName || lastTag?.tagDisplayName;

  return (
    <div
      ref={setNodeRef}
      onClick={() => window.open(`https://www.acmicpc.net/problem/${problem.problemId}`, '_blank')}
      style={style}
      className="bg-background relative flex cursor-pointer items-center rounded-md px-1 py-2 text-xs"
    >
      {/* 드래그 핸들 */}
      <AppTooltip content="문제 순서 변경" side="right">
        <button {...attributes} {...listeners} className="text-muted-foreground hover:text-foreground mr-1 cursor-grab active:cursor-grabbing" aria-label="문제 순서 변경">
          <GripVertical className="h-4 w-4" />
        </button>
      </AppTooltip>

      {/* 문제 기본정보 */}
      {(showFilters.algorithm || showFilters.problemTier || showFilters.problemNumber) && (
        <div className="mr-2 flex max-w-[calc(50%-10px)] flex-col gap-1 text-center">
          {showFilters.algorithm && lastTag && (
            <Popover open={isTagOpen} onOpenChange={setIsTagOpen}>
              <PopoverTrigger asChild>
                <div
                  className={`group relative flex items-center gap-1 rounded px-2 py-0.5 ${!isSolved ? 'bg-innerground-darkgray' : tagInfo ? tagInfo.bgColor : 'bg-logo'}`}
                  onClick={(e) => e.stopPropagation()}
                >
                  <span className="line-clamp-1">{tagDisplayName}</span>
                  <PencilLine className="text-muted-foreground group-hover:text-primary h-2 w-2" />
                </div>
              </PopoverTrigger>
              <PopoverContent className="w-fit p-2" side="top" align="start" onClick={(e) => e.stopPropagation()}>
                <div className="flex flex-col items-start gap-0.5 text-xs">
                  {problem.tags.map((onetag) => (
                    <div
                      key={onetag.tagCode}
                      aria-label={onetag.tagCode}
                      className="hover:bg-background w-full cursor-pointer rounded px-1 text-start"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleRepresentativeTag(onetag.tagCode);
                      }}
                    >
                      {TAG_INFO[onetag.tagCode] ? TAG_INFO[onetag.tagCode].kr : onetag.tagDisplayName}
                    </div>
                  ))}
                </div>
              </PopoverContent>
            </Popover>
          )}
          {showFilters.algorithm && !lastTag && <div className={`rounded px-2 py-0.5 ${isSolved && tagInfo ? tagInfo.bgColor : 'bg-gray-300'}`}>Undefined</div>}
          {(showFilters.problemTier || showFilters.problemNumber) && (
            <div className="flex items-center gap-1">
              {showFilters.problemTier && <Image src={`/tiers/tier_${problem.problemTierLevel}.svg`} alt={`Tier ${problem.problemTierLevel}`} width={12} height={12} />}
              {showFilters.problemNumber && <span>{problem.problemId}</span>}
            </div>
          )}
        </div>
      )}

      {/* 문제이름 */}
      <div className="line-clamp-2 flex-1 pr-4 text-end">{problem.problemTitle}</div>

      {/* 삭제 버튼 (willSolve만) */}
      {!isSolved && onDelete && (
        <AppTooltip content="문제 삭제" side="left">
          <button
            onClick={(e) => {
              e.stopPropagation();
              onDelete();
            }}
            className="text-muted-foreground hover:text-destructive absolute top-0 right-0 shrink-0 rounded p-1 transition-colors"
            aria-label="문제 삭제"
          >
            <X className="h-4 w-4" />
          </button>
        </AppTooltip>
      )}
    </div>
  );
}

// 검색 결과 문제 카드 (클릭 가능)
function SearchResultCard({ problem, onClick, showFilters }: { problem: WillSolveProblems; onClick: () => void; showFilters: SidebarShowFilters }) {
  const firstTag = problem.tags[0];
  const lastTag = problem.tags.length > 0 ? problem.tags[problem.tags.length - 1] : null;
  const tagInfo = TAG_INFO[problem.representativeTag?.tagCode || lastTag?.tagCode || firstTag?.tagCode];

  return (
    <button onClick={onClick} className="bg-background hover:bg-accent flex w-full items-center gap-2 rounded-md p-2 text-left text-xs transition-colors">
      {/* 문제 기본정보 */}
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

      {/* 문제이름 */}
      <div className="line-clamp-2 flex-1 text-end">{problem.problemTitle}</div>
    </button>
  );
}

export function CalendarSidebarInset({ isLanding = false, calendarData }: { calendarData?: Calendar; isLanding?: boolean }) {
  const { selectedDate } = useCalendarStore();
  const { showFilters, toggleFilter, resetFilters } = useCalendarSidebarStore();
  const [showAddInput, setShowAddInput] = useState(false);
  const [showFilterSection, setShowFilterSection] = useState(false);
  const [searchKeyword, setSearchKeyword] = useState('');
  const [debouncedKeyword, setDebouncedKeyword] = useState('');
  const solvedContextId = useId(); // DndContext
  const willsolveContextId = useId();

  // 현재 선택된 날짜의 년/월로 calendar 데이터 fetch
  // const year = selectedDate?.getFullYear() || new Date().getFullYear();
  // const month = (selectedDate?.getMonth() || new Date().getMonth()) + 1;
  // const { data: calendarData } = useCalendar(year, month);

  const updateWillSolve = useUpdateWillSolveProblems({
    onError: (error) => {
      const errorCode = getErrorCode(error);
      const errorMessage = errorCode === 'ALREADY_SOLVED_PROBLEM' ? getErrorMessage(error) : '이미 추가한 문제입니다.';
      toast.error(errorMessage);
    },
  });
  const updateSolved = useUpdateSolvedProblems();
  const updateRepresentativeTag = useUpdateRepresentativeTag({
    onSuccess: () => {
      toast.success('대표 태그 변경 완료!');
    },
    onError: () => {
      toast.error('대표 태그 변경에 실패했습니다.');
    },
  });

  // Debounce 로직 (400ms)
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedKeyword(searchKeyword);
    }, 400);

    return () => clearTimeout(timer);
  }, [searchKeyword]);

  // 검색 API 호출
  const { data: searchResults, isLoading: isSearching } = useSearchProblems(debouncedKeyword);

  // selectedDate에 해당하는 문제 목록 필터링
  const solvedProblems = useMemo(() => {
    if (!calendarData || !selectedDate) return [];
    const dateString = formatDateString(selectedDate);
    const dayData = calendarData.monthlyData.find((d) => d.targetDate === dateString);
    return dayData?.solvedProblems || [];
  }, [calendarData, selectedDate]);

  const willSolveProblems = useMemo(() => {
    if (!calendarData || !selectedDate) return [];
    const dateString = formatDateString(selectedDate);
    const dayData = calendarData.monthlyData.find((d) => d.targetDate === dateString);
    return dayData?.willSolveProblems || [];
  }, [calendarData, selectedDate]);

  // 드래그 센서 설정
  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 8, // 8px 이동 후 드래그 시작
      },
    }),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    }),
  );

  // Solved 문제 순서 변경
  const handleSolvedDragEnd = (event: DragEndEvent) => {
    if (isLanding) {
      toast.info('로그인 후 이용해주세요');
      return;
    }
    const { active, over } = event;

    if (!over || active.id === over.id || !selectedDate) return;

    const oldIndex = solvedProblems.findIndex((p) => p.problemId === active.id);
    const newIndex = solvedProblems.findIndex((p) => p.problemId === over.id);

    const reorderedProblems = arrayMove(solvedProblems, oldIndex, newIndex);
    const problemId = reorderedProblems.map((p) => p.problemId);

    updateSolved.mutate({
      date: formatDateString(selectedDate),
      problemId,
    });
  };

  // WillSolve 문제 순서 변경
  const handleWillSolveDragEnd = (event: DragEndEvent) => {
    if (isLanding) {
      toast.info('로그인 후 이용해주세요');
      return;
    }
    const { active, over } = event;

    if (!over || active.id === over.id || !selectedDate) return;

    const oldIndex = willSolveProblems.findIndex((p) => p.problemId === active.id);
    const newIndex = willSolveProblems.findIndex((p) => p.problemId === over.id);

    const reorderedProblems = arrayMove(willSolveProblems, oldIndex, newIndex);
    const problemIds = reorderedProblems.map((p) => p.problemId);

    updateWillSolve.mutate({
      date: formatDateString(selectedDate),
      problemIds,
    });
  };

  // WillSolve 문제 추가 (검색 결과 클릭 시)
  const handleAddProblemFromSearch = (problemId: number) => {
    if (isLanding) {
      toast.info('로그인 후 이용해주세요');
      return;
    }
    if (!selectedDate) return;

    // 검색 결과에서 추가할 문제 찾기
    const problemToAdd = uniqueSearchResults.find((p) => p.problemId === problemId);
    if (!problemToAdd) return;

    // 기존 문제들 + 새 문제
    const problemIds = [...willSolveProblems.map((p) => p.problemId), problemId];

    updateWillSolve.mutate(
      {
        date: formatDateString(selectedDate),
        problemIds,
        newProblems: [problemToAdd], // 낙관적 업데이트를 위한 새 문제 정보
      },
      {
        onSuccess: () => {
          setSearchKeyword('');
          setShowAddInput(false);
          toast.success('문제 추가 완료!');
        },
      },
    );
  };

  // WillSolve 문제 삭제
  const handleDeleteProblem = (problemId: number) => {
    if (isLanding) {
      toast.info('로그인 후 이용해주세요');
      return;
    }
    if (!selectedDate) return;

    const problemIds = willSolveProblems.filter((p) => p.problemId !== problemId).map((p) => p.problemId);

    updateWillSolve.mutate(
      {
        date: formatDateString(selectedDate),
        problemIds,
      },
      {
        onSuccess: () => {
          toast.success('문제 삭제 완료!');
        },
      },
    );
  };

  // 문제 대표태그 변경
  const handleUpdateRepresentativeTag = (problemId: number, tagCode: string) => {
    if (isLanding) {
      toast.info('로그인 후 이용해주세요');
      return;
    }
    if (!selectedDate) return;

    updateRepresentativeTag.mutate({
      date: formatDateString(selectedDate),
      problemId,
      representativeTagCode: tagCode,
    });
  };

  // 검색 결과 병합 (idBase + titleBase)
  const allSearchResults = searchResults ? [...searchResults.problems.idBase, ...searchResults.problems.titleBase] : [];

  // 중복 제거 (problemId 기준)
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
      {/* Solved 문제 목록 */}
      <div className="flex cursor-default flex-col gap-2" data-onboarding-id="calendar-sidebar-solved">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-semibold">해결한 문제</h3>
          <div className="flex items-center gap-2">
            <span className="text-xs text-gray-500">{solvedProblems.length}개</span>
            <HelpPopover width="w-85">
              <div className="space-y-2">
                <h4 className="text-sm font-semibold">
                  선택한 날짜에 <span className="text-primary font-semibold">풀었던</span> 문제가 기록됩니다.
                </h4>
                <p className="text-muted-foreground text-xs">
                  가입 전에 풀었던 문제는 <span className="text-primary font-semibold">가입 전 풀이 등록하기</span>로 등록해 주세요.
                </p>
                <p className="text-muted-foreground text-xs">
                  새로 푼 문제가 보이지 않는다면, <span className="text-primary font-semibold">Refresh</span> 버튼을 눌러주세요 .
                </p>
              </div>
            </HelpPopover>
          </div>
        </div>

        {solvedProblems.length === 0 ? (
          <div className="rounded-lg border border-dashed border-gray-300 p-4 text-center text-xs text-gray-400">풀이한 문제가 없습니다</div>
        ) : (
          <DndContext id={solvedContextId} sensors={sensors} collisionDetection={closestCenter} onDragEnd={handleSolvedDragEnd}>
            <SortableContext items={solvedProblems.map((p) => p.problemId)} strategy={verticalListSortingStrategy}>
              <div className="flex flex-col gap-2">
                {solvedProblems.map((problem) => (
                  <DraggableProblemCard
                    key={problem.problemId}
                    problem={problem}
                    isSolved={true}
                    onUpdateRepresentativeTag={(tagCode) => handleUpdateRepresentativeTag(problem.problemId, tagCode)}
                    showFilters={showFilters}
                  />
                ))}
              </div>
            </SortableContext>
          </DndContext>
        )}
      </div>

      {/* Will Solve 문제 목록 */}
      <div className="flex cursor-default flex-col gap-2" data-onboarding-id="calendar-sidebar-scheduled">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-semibold">오늘의 일정</h3>
          <div className="flex items-center gap-2">
            <span className="text-xs text-gray-500">{willSolveProblems.length}개</span>
            <HelpPopover>
              <div className="space-y-2">
                <h4 className="text-sm font-semibold">
                  선택한 날짜에 <span className="text-primary font-semibold">일정 등록한</span> 문제가 기록됩니다.
                </h4>
                <p className="text-muted-foreground text-xs">풀어야 할 문제들을 등록해보세요.</p>
                <p className="text-muted-foreground text-xs">
                  실제로 문제를 푼 뒤 <span className="text-primary font-semibold">Refresh</span> 버튼을 누르면, 해결한 문제로 등록됩니다.
                </p>
              </div>
            </HelpPopover>
          </div>
        </div>

        {willSolveProblems.length === 0 ? (
          <div className="rounded-lg border border-dashed border-gray-300 p-4 text-center text-xs text-gray-400">예약된 문제가 없습니다</div>
        ) : (
          <DndContext id={willsolveContextId} sensors={sensors} collisionDetection={closestCenter} onDragEnd={handleWillSolveDragEnd}>
            <SortableContext items={willSolveProblems.map((p) => p.problemId)} strategy={verticalListSortingStrategy}>
              <div className="flex flex-col gap-2">
                {willSolveProblems.map((problem) => (
                  <DraggableProblemCard
                    key={problem.problemId}
                    problem={problem}
                    isSolved={false}
                    onDelete={() => handleDeleteProblem(problem.problemId)}
                    onUpdateRepresentativeTag={(tagCode) => handleUpdateRepresentativeTag(problem.problemId, tagCode)}
                    showFilters={showFilters}
                  />
                ))}
              </div>
            </SortableContext>
          </DndContext>
        )}

        {/* 문제 추가하기 */}
        {!showAddInput ? (
          <button onClick={() => setShowAddInput(true)} disabled={isLanding} className="hover:bg-innerground-hovergray text-muted-foreground my-4 cursor-pointer rounded px-2 py-2 text-start text-sm">
            + 오늘 풀 문제 등록하기
          </button>
        ) : (
          <div className="my-4 flex flex-col gap-2">
            {/* 검색창 */}
            <div className="relative">
              <Search className="text-muted-foreground absolute top-1/2 left-2 h-4 w-4 -translate-y-1/2" aria-label="문제 검색" />
              <input
                type="text"
                value={searchKeyword}
                onChange={(e) => setSearchKeyword(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Escape') {
                    setShowAddInput(false);
                    setSearchKeyword('');
                  }
                }}
                placeholder="문제 검색..."
                className="border-input bg-background focus:ring-ring w-full rounded border py-2 pr-3 pl-8 text-sm focus:ring-2 focus:outline-none"
                autoFocus
              />
            </div>

            {/* 검색 결과 */}
            {searchKeyword.trim().length > 0 && (
              <div className="border-input hide-scrollbar max-h-60 overflow-y-auto rounded border">
                {isSearching ? (
                  <div className="p-4 text-center text-xs text-gray-400">검색 중...</div>
                ) : uniqueSearchResults.length === 0 ? (
                  <div className="p-4 text-center text-xs text-gray-400">검색 결과가 없습니다</div>
                ) : (
                  <div>
                    <div className="pt-2 pl-2 text-xs font-semibold">문제 ({uniqueSearchResults.length})</div>

                    <div className="flex flex-col gap-1 p-2">
                      {uniqueSearchResults.map((problem) => (
                        <SearchResultCard key={problem.problemId} problem={problem} onClick={() => handleAddProblemFromSearch(problem.problemId)} showFilters={showFilters} />
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* 취소 버튼 */}
            <button
              onClick={() => {
                setShowAddInput(false);
                setSearchKeyword('');
              }}
              className="bg-secondary text-secondary-foreground hover:bg-secondary/80 rounded px-3 py-2 text-sm"
            >
              취소
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
