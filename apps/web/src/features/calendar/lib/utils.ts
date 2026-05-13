import { CalendarEvent, MonthlyData, SolvedProblems, WillSolveProblems } from '@/entities/calendar';

/**
 * MonthlyData 배열을 react-big-calendar 이벤트 형식으로 변환
 */
export function transformToCalendarEvents(monthlyDataArray: MonthlyData[]): CalendarEvent[] {
  const events: CalendarEvent[] = [];

  monthlyDataArray.forEach((dayData: MonthlyData) => {
    const date = new Date(dayData.targetDate);

    // solved 문제들을 이벤트로 변환
    dayData.solvedProblems.forEach((problem: SolvedProblems) => {
      const lastTagDisplayName = problem.tags.length > 0 ? problem.tags[problem.tags.length - 1].tagDisplayName : '';
      const lastTagCode = problem.tags.length > 0 ? problem.tags[problem.tags.length - 1].tagCode : '';
      if (problem.tags.length > 0) {
        events.push({
          title: problem.representativeTag?.tagDisplayName || lastTagDisplayName,
          start: date,
          end: date,
          resource: {
            type: 'solved',
            problem,
            tagCode: problem.representativeTag?.tagCode || lastTagCode,
          },
        });
      }
    });

    // will solve 문제들을 이벤트로 변환
    dayData.willSolveProblems.forEach((problem: WillSolveProblems) => {
      const lastTagDisplayName = problem.tags.length > 0 ? problem.tags[problem.tags.length - 1].tagDisplayName : '';
      const lastTagCode = problem.tags.length > 0 ? problem.tags[problem.tags.length - 1].tagCode : '';
      if (problem.tags.length > 0) {
        events.push({
          title: problem.representativeTag?.tagDisplayName || lastTagDisplayName,
          start: date,
          end: date,
          resource: {
            type: 'willSolve',
            problem,
            tagCode: problem.representativeTag?.tagCode || lastTagCode,
          },
        });
      }
    });
  });

  return events;
}

/**
 * 특정 날짜의 이벤트들을 그룹핑하여 표시할 태그 목록 반환
 * - 최대 3개 표시 (solved 우선, will solve는 회색)
 * - 4개 이상이면 2개 표시 + "n개 더보기"
 */
export function getDisplayTags(events: CalendarEvent[]) {
  const MAX_DISPLAY = 3;

  // solved와 willSolve를 분리하고, solved를 우선순위로
  const solvedEvents = events.filter((e) => e.resource.type === 'solved');
  const willSolveEvents = events.filter((e) => e.resource.type === 'willSolve');

  const allTags = [...solvedEvents, ...willSolveEvents];
  const totalCount = allTags.length;

  if (totalCount === 0) {
    return { displayTags: [], hasMore: false, moreCount: 0 };
  }

  // 4개 이상이면 2개만 표시하고 "n개 더보기"
  if (totalCount > MAX_DISPLAY) {
    return {
      displayTags: allTags.slice(0, 2),
      hasMore: true,
      moreCount: totalCount - 2,
    };
  }

  // 3개 이하면 모두 표시
  return {
    displayTags: allTags.slice(0, MAX_DISPLAY),
    hasMore: false,
    moreCount: 0,
  };
}
