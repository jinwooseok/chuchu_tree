'use client';

import dynamic from 'next/dynamic';
import { useCalendarStore } from '@/lib/store/calendar';
import { TAG_INFO } from '@/shared/constants/tagSystem';
import { Problem } from '@/shared/types/calendar';
import { format } from 'date-fns';
import { ko } from 'date-fns/locale';

// 클라이언트 전용 렌더링 (hydration mismatch 방지)
const SmallCalendar = dynamic(() => import('@/features/calendar/ui/SmallCalendar'), {
  ssr: false,
  loading: () => (
    <div className="flex items-center justify-center" style={{ minHeight: '300px' }}>
      <div className="text-sm text-gray-400">Loading...</div>
    </div>
  ),
});

// 개별 문제 카드 컴포넌트
function ProblemCard({ problem, isSolved }: { problem: Problem; isSolved: boolean }) {
  const firstTag = problem.tags[0];
  const tagInfo = TAG_INFO[firstTag?.tagCode as keyof typeof TAG_INFO];

  // will solve는 회색, solved는 tag별 색상
  const bgColorClass = isSolved && tagInfo ? tagInfo.bgColor : 'bg-gray-300';

  return (
    <div className="rounded-lg border border-gray-200 p-3 hover:bg-gray-50">
      {/* 문제 제목 */}
      <div className="mb-2 text-sm font-medium">{problem.problemTitle}</div>

      {/* 문제 ID와 티어 */}
      <div className="mb-2 flex items-center gap-2 text-xs text-gray-600">
        <span>#{problem.problemId}</span>
        <span>•</span>
        <span>{problem.problemTierName}</span>
      </div>

      {/* 태그 목록 */}
      <div className="flex flex-wrap gap-1">
        {problem.tags.map((tag) => {
          const tagInfo = TAG_INFO[tag.tagCode as keyof typeof TAG_INFO];
          const bgColor = isSolved && tagInfo ? tagInfo.bgColor : 'bg-gray-300';

          return (
            <span key={tag.tagId} className={`rounded px-2 py-0.5 text-xs ${bgColor}`}>
              {tag.tagDisplayName}
            </span>
          );
        })}
      </div>
    </div>
  );
}

export default function CalendarSidebar() {
  const selectedDate = useCalendarStore((state) => state.selectedDate);
  const getSolvedProblems = useCalendarStore((state) => state.getSolvedProblemsByDate);
  const getWillSolveProblems = useCalendarStore((state) => state.getWillSolveProblemsByDate);

  const solvedProblems = getSolvedProblems(selectedDate);
  const willSolveProblems = getWillSolveProblems(selectedDate);

  return (
    <div className="flex h-full flex-col gap-4 overflow-y-auto p-4">
      {/* 미니 캘린더 */}
      <div>
        <SmallCalendar />
      </div>

      {/* 선택된 날짜 표시 */}
      <div className="text-center text-sm font-semibold text-gray-700" suppressHydrationWarning>
        {format(selectedDate, 'yyyy년 M월 d일 (eee)', { locale: ko })}
      </div>

      {/* Solved 문제 목록 */}
      <div className="flex flex-col gap-2">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-semibold">Solved</h3>
          <span className="text-xs text-gray-500">{solvedProblems.length}개</span>
        </div>

        {solvedProblems.length === 0 ? (
          <div className="rounded-lg border border-dashed border-gray-300 p-4 text-center text-xs text-gray-400">풀이한 문제가 없습니다</div>
        ) : (
          <div className="flex flex-col gap-2">
            {solvedProblems.map((problem) => (
              <ProblemCard key={problem.problemId} problem={problem} isSolved={true} />
            ))}
          </div>
        )}
      </div>

      {/* Will Solve 문제 목록 */}
      <div className="flex flex-col gap-2">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-semibold">Will Solve</h3>
          <span className="text-xs text-gray-500">{willSolveProblems.length}개</span>
        </div>

        {willSolveProblems.length === 0 ? (
          <div className="rounded-lg border border-dashed border-gray-300 p-4 text-center text-xs text-gray-400">예약된 문제가 없습니다</div>
        ) : (
          <div className="flex flex-col gap-2">
            {willSolveProblems.map((problem) => (
              <ProblemCard key={problem.problemId} problem={problem} isSolved={false} />
            ))}
          </div>
        )}
      </div>

      {/* 문제 추가하기 버튼 (향후 구현) */}
      <button className="mt-2 rounded-lg border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50">
        + 문제 추가하기
      </button>
    </div>
  );
}
