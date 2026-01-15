'use client';

import dynamic from 'next/dynamic';
import { useCalendarStore } from '@/lib/store/calendar';
import { TAG_INFO } from '@/shared/constants/tagSystem';
import { Problem, useUpdateWillSolveProblems, useUpdateSolvedProblems, useSearchProblems, WillSolveProblems, useCalendar } from '@/entities/calendar';
import Image from 'next/image';
import { useState, useEffect, useMemo, useId } from 'react';
import { DndContext, closestCenter, KeyboardSensor, PointerSensor, useSensor, useSensors, DragEndEvent } from '@dnd-kit/core';
import { arrayMove, SortableContext, sortableKeyboardCoordinates, useSortable, verticalListSortingStrategy } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import { GripVertical, X, Search } from 'lucide-react';
import { toast } from 'sonner';
import { AppTooltip } from '@/components/custom/tooltip/AppTooltip';

// 클라이언트 전용 렌더링 (hydration mismatch 방지)
const SmallCalendar = dynamic(() => import('@/features/calendar/ui/SmallCalendar'), {
  ssr: false,
  loading: () => (
    <div className="flex items-center justify-center" style={{ minHeight: '300px' }}>
      <div className="text-sm text-gray-400">Loading...</div>
    </div>
  ),
});

// 날짜를 YYYY-MM-DD 형식으로 변환
const formatDateString = (date: Date): string => {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
};

// 드래그 가능한 문제 카드
function DraggableProblemCard({ problem, isSolved, onDelete }: { problem: Problem; isSolved: boolean; onDelete?: () => void }) {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({ id: problem.problemId });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
  };

  const firstTag = problem.tags[0];
  const tagInfo = TAG_INFO[firstTag?.tagCode as keyof typeof TAG_INFO];

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
      <div className="mr-2 flex shrink-0 flex-col gap-1 text-center">
        {firstTag && <div className={`rounded px-2 py-0.5 ${isSolved && tagInfo ? tagInfo.bgColor : 'bg-gray-300'}`}>{firstTag.tagDisplayName}</div>}
        {!firstTag && <div className={`rounded px-2 py-0.5 ${isSolved && tagInfo ? tagInfo.bgColor : 'bg-gray-300'}`}>Undefined</div>}
        <div className="flex items-center gap-1">
          <Image src={`/tiers/tier_${problem.problemTierLevel}.svg`} alt={`Tier ${problem.problemTierLevel}`} width={24} height={24} className="h-4 w-4" />
          <span>{problem.problemId}</span>
        </div>
      </div>

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
function SearchResultCard({ problem, onClick }: { problem: WillSolveProblems; onClick: () => void }) {
  const firstTag = problem.tags[0];
  const tagInfo = TAG_INFO[firstTag?.tagCode as keyof typeof TAG_INFO];

  return (
    <button onClick={onClick} className="bg-background hover:bg-accent flex w-full items-center gap-2 rounded-md p-2 text-left text-xs transition-colors">
      {/* 문제 기본정보 */}
      <div className="flex shrink-0 flex-col gap-1 text-center">
        {firstTag && <div className={`rounded px-2 py-0.5 ${tagInfo ? tagInfo.bgColor : 'bg-gray-300'}`}>{firstTag.tagDisplayName}</div>}
        {!firstTag && <div className="rounded bg-gray-300 px-2 py-0.5">Undefined</div>}
        <div className="flex items-center gap-1">
          <Image src={`/tiers/tier_${problem.problemTierLevel}.svg`} alt={`Tier ${problem.problemTierLevel}`} width={24} height={24} className="h-4 w-4" />
          <span>{problem.problemId}</span>
        </div>
      </div>

      {/* 문제이름 */}
      <div className="line-clamp-2 flex-1 text-end">{problem.problemTitle}</div>
    </button>
  );
}

export default function CalendarSidebar() {
  const { selectedDate } = useCalendarStore();
  const [showAddInput, setShowAddInput] = useState(false);
  const [searchKeyword, setSearchKeyword] = useState('');
  const [debouncedKeyword, setDebouncedKeyword] = useState('');
  const solvedContextId = useId(); // DndContext
  const willsolveContextId = useId();

  // 현재 선택된 날짜의 년/월로 calendar 데이터 fetch
  const year = selectedDate?.getFullYear() || new Date().getFullYear();
  const month = (selectedDate?.getMonth() || new Date().getMonth()) + 1;
  const { data: calendarData } = useCalendar(year, month);

  const updateWillSolve = useUpdateWillSolveProblems({
    onError: (error: any) => {
      const errorMessage = error?.response?.data?.message || '업데이트에 실패했습니다.';
      toast.error(errorMessage, {
        position: 'top-center',
      });
    },
  });
  const updateSolved = useUpdateSolvedProblems();

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
    const { active, over } = event;

    if (!over || active.id === over.id || !selectedDate) return;

    const oldIndex = solvedProblems.findIndex((p) => p.problemId === active.id);
    const newIndex = solvedProblems.findIndex((p) => p.problemId === over.id);

    const reorderedProblems = arrayMove(solvedProblems, oldIndex, newIndex);
    const problemIds = reorderedProblems.map((p) => p.problemId);

    updateSolved.mutate({
      date: formatDateString(selectedDate),
      problemIds,
    });
  };

  // WillSolve 문제 순서 변경
  const handleWillSolveDragEnd = (event: DragEndEvent) => {
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
          toast.success('문제 추가 완료!', {
            position: 'top-center',
          });
        },
      },
    );
  };

  // WillSolve 문제 삭제
  const handleDeleteProblem = (problemId: number) => {
    if (!selectedDate) return;

    const problemIds = willSolveProblems.filter((p) => p.problemId !== problemId).map((p) => p.problemId);

    updateWillSolve.mutate(
      {
        date: formatDateString(selectedDate),
        problemIds,
      },
      {
        onSuccess: () => {
          toast.success('문제 삭제 완료!', {
            position: 'top-center',
          });
        },
      },
    );
  };

  // 검색 결과 병합 (idBase + titleBase)
  const allSearchResults = searchResults ? [...searchResults.problems.idBase, ...searchResults.problems.titleBase] : [];

  // 중복 제거 (problemId 기준)
  const uniqueSearchResults = Array.from(new Map(allSearchResults.map((p) => [p.problemId, p])).values());

  return (
    <div className="hide-scrollbar flex h-full flex-col gap-8 overflow-y-auto p-4">
      {/* 미니 캘린더 */}
      <div>
        <SmallCalendar />
      </div>

      {/* Solved 문제 목록 */}
      <div className="flex cursor-default flex-col gap-2">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-semibold">해결한 문제</h3>
          <span className="text-xs text-gray-500">{solvedProblems.length}개</span>
        </div>

        {solvedProblems.length === 0 ? (
          <div className="rounded-lg border border-dashed border-gray-300 p-4 text-center text-xs text-gray-400">풀이한 문제가 없습니다</div>
        ) : (
          <DndContext id={solvedContextId} sensors={sensors} collisionDetection={closestCenter} onDragEnd={handleSolvedDragEnd}>
            <SortableContext items={solvedProblems.map((p) => p.problemId)} strategy={verticalListSortingStrategy}>
              <div className="flex flex-col gap-2">
                {solvedProblems.map((problem) => (
                  <DraggableProblemCard key={problem.problemId} problem={problem} isSolved={true} />
                ))}
              </div>
            </SortableContext>
          </DndContext>
        )}
      </div>

      {/* Will Solve 문제 목록 */}
      <div className="flex cursor-default flex-col gap-2">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-semibold">오늘의 일정</h3>
          <span className="text-xs text-gray-500">{willSolveProblems.length}개</span>
        </div>

        {willSolveProblems.length === 0 ? (
          <div className="rounded-lg border border-dashed border-gray-300 p-4 text-center text-xs text-gray-400">예약된 문제가 없습니다</div>
        ) : (
          <DndContext id={willsolveContextId} sensors={sensors} collisionDetection={closestCenter} onDragEnd={handleWillSolveDragEnd}>
            <SortableContext items={willSolveProblems.map((p) => p.problemId)} strategy={verticalListSortingStrategy}>
              <div className="flex flex-col gap-2">
                {willSolveProblems.map((problem) => (
                  <DraggableProblemCard key={problem.problemId} problem={problem} isSolved={false} onDelete={() => handleDeleteProblem(problem.problemId)} />
                ))}
              </div>
            </SortableContext>
          </DndContext>
        )}

        {/* 문제 추가하기 */}
        {!showAddInput ? (
          <button onClick={() => setShowAddInput(true)} className="hover:bg-background text-muted-foreground my-4 cursor-pointer rounded px-2 py-2 text-start text-sm">
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
                        <SearchResultCard key={problem.problemId} problem={problem} onClick={() => handleAddProblemFromSearch(problem.problemId)} />
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
