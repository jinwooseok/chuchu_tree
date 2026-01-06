'use client';

import dynamic from 'next/dynamic';
import { useCalendarStore } from '@/lib/store/calendar';
import { TAG_INFO } from '@/shared/constants/tagSystem';
import { Problem, useUpdateWillSolveProblems, useUpdateSolvedProblems } from '@/entities/calendar';
import Image from 'next/image';
import { useState } from 'react';
import { DndContext, closestCenter, KeyboardSensor, PointerSensor, useSensor, useSensors, DragEndEvent } from '@dnd-kit/core';
import { arrayMove, SortableContext, sortableKeyboardCoordinates, useSortable, verticalListSortingStrategy } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import { GripVertical, X } from 'lucide-react';

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
    <div ref={setNodeRef} style={style} className="bg-background flex items-center gap-2 rounded-md p-2 text-xs">
      {/* 드래그 핸들 */}
      <button {...attributes} {...listeners} className="text-muted-foreground hover:text-foreground cursor-grab active:cursor-grabbing">
        <GripVertical className="h-4 w-4" />
      </button>

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
      <div className="line-clamp-2 flex-1">{problem.problemTitle}</div>

      {/* 삭제 버튼 (willSolve만) */}
      {!isSolved && onDelete && (
        <button onClick={onDelete} className="text-muted-foreground hover:text-destructive shrink-0 rounded p-1 transition-colors" title="삭제">
          <X className="h-4 w-4" />
        </button>
      )}
    </div>
  );
}

export default function CalendarSidebar() {
  const { selectedDate, getSolvedProblemsByDate, getWillSolveProblemsByDate } = useCalendarStore();
  const [showAddInput, setShowAddInput] = useState(false);
  const [newProblemId, setNewProblemId] = useState('');

  const updateWillSolve = useUpdateWillSolveProblems();
  const updateSolved = useUpdateSolvedProblems();

  // selectedDate가 null일 경우 빈 배열 반환
  const solvedProblems = selectedDate ? getSolvedProblemsByDate(selectedDate) : [];
  const willSolveProblems = selectedDate ? getWillSolveProblemsByDate(selectedDate) : [];

  // 드래그 센서 설정
  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 8, // 8px 이동 후 드래그 시작
      },
    }),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
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

  // WillSolve 문제 추가
  const handleAddProblem = () => {
    const problemId = parseInt(newProblemId.trim(), 10);

    if (!problemId || isNaN(problemId) || !selectedDate) {
      alert('올바른 문제 번호를 입력해주세요.');
      return;
    }

    // 기존 문제들 + 새 문제
    const problemIds = [...willSolveProblems.map((p) => p.problemId), problemId];

    updateWillSolve.mutate(
      {
        date: formatDateString(selectedDate),
        problemIds,
      },
      {
        onSuccess: () => {
          setNewProblemId('');
          setShowAddInput(false);
        },
        onError: () => {
          alert('문제 추가에 실패했습니다.');
        },
      }
    );
  };

  // WillSolve 문제 삭제
  const handleDeleteProblem = (problemId: number) => {
    if (!selectedDate) return;

    const problemIds = willSolveProblems.filter((p) => p.problemId !== problemId).map((p) => p.problemId);

    updateWillSolve.mutate({
      date: formatDateString(selectedDate),
      problemIds,
    });
  };

  return (
    <div className="flex h-full flex-col gap-8 overflow-y-auto p-4">
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
          <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={handleSolvedDragEnd}>
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
          <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={handleWillSolveDragEnd}>
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
          <button onClick={() => setShowAddInput(true)} className="hover:bg-background text-muted-foreground mb-4 cursor-pointer rounded px-2 py-2 text-start text-sm">
            + 오늘 풀 문제 등록하기
          </button>
        ) : (
          <div className="mb-4 flex gap-2">
            <input
              type="text"
              value={newProblemId}
              onChange={(e) => setNewProblemId(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') handleAddProblem();
                if (e.key === 'Escape') {
                  setShowAddInput(false);
                  setNewProblemId('');
                }
              }}
              placeholder="문제 번호 입력"
              className="border-input bg-background focus:ring-ring flex-1 rounded border px-3 py-2 text-sm focus:outline-none focus:ring-2"
              autoFocus
            />
            <button onClick={handleAddProblem} className="bg-primary text-primary-foreground hover:bg-primary/90 rounded px-3 py-2 text-sm">
              추가
            </button>
            <button
              onClick={() => {
                setShowAddInput(false);
                setNewProblemId('');
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
