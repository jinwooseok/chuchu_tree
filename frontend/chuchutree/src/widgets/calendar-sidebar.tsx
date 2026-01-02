'use client';

import dynamic from 'next/dynamic';
import { useCalendarStore } from '@/lib/store/calendar';
import { TAG_INFO } from '@/shared/constants/tagSystem';
import { Problem } from '@/shared/types/calendar';
import Image from 'next/image';

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

  return (
    <div className="bg-background flex items-center justify-between rounded-md p-2 text-xs">
      {/* 문제기본정보 */}
      <div className="mr-4 flex shrink-0 flex-col gap-1 text-center">
        <div className={`rounded px-2 py-0.5 ${isSolved && tagInfo ? tagInfo.bgColor : 'bg-gray-300'}`}>{firstTag.tagDisplayName}</div>
        <div className="flex items-center gap-1">
          <Image src={`/tiers/tier_${problem.problemTierLevel}.svg`} alt={`Tier ${problem.problemTierLevel}`} width={24} height={24} className="h-4 w-4" />
          <span>{problem.problemId}</span>
        </div>
      </div>
      {/* 문제이름 */}
      <div className="line-clamp-2">{problem.problemTitle}</div>
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
          <div className="flex flex-col gap-2">
            {solvedProblems.map((problem) => (
              <ProblemCard key={problem.problemId} problem={problem} isSolved={true} />
            ))}
          </div>
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
          <div className="flex flex-col gap-2">
            {willSolveProblems.map((problem) => (
              <ProblemCard key={problem.problemId} problem={problem} isSolved={false} />
            ))}
          </div>
        )}
        {/* 문제 추가하기 버튼 (향후 구현) */}
        <button className="hover:bg-background text-muted-foreground mb-4 cursor-pointer rounded px-2 py-2 text-start text-sm">+ 오늘 풀 문제 등록하기</button>
      </div>
    </div>
  );
}
