import { CalendarApiResponse, CalendarEvent, MonthlyData, Problem } from '@/shared/types/calendar';

/**
 * API 응답 데이터 또는 MonthlyData 배열을 react-big-calendar 이벤트 형식으로 변환
 */
export function transformToCalendarEvents(data: CalendarApiResponse | MonthlyData[]): CalendarEvent[] {
  const events: CalendarEvent[] = [];

  // CalendarApiResponse인지 MonthlyData[]인지 확인
  const monthlyDataArray = Array.isArray(data) ? data : data.data.monthlyData;

  monthlyDataArray.forEach((dayData: MonthlyData) => {
    const date = new Date(dayData.date);

    // solved 문제들을 이벤트로 변환
    dayData.solvedProblems.forEach((problem: Problem) => {
      problem.tags.forEach((tag) => {
        events.push({
          title: tag.tagDisplayName,
          start: date,
          end: date,
          resource: {
            type: 'solved',
            problem,
            tagCode: tag.tagCode,
          },
        });
      });
    });

    // will solve 문제들을 이벤트로 변환
    dayData.willSolveProblem.forEach((problem: Problem) => {
      problem.tags.forEach((tag) => {
        events.push({
          title: tag.tagDisplayName,
          start: date,
          end: date,
          resource: {
            type: 'willSolve',
            problem,
            tagCode: tag.tagCode,
          },
        });
      });
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

  // 중복 제거 (같은 tagCode는 한 번만 표시)
  const uniqueSolved = Array.from(new Map(solvedEvents.map((e) => [e.resource.tagCode, e])).values());
  const uniqueWillSolve = Array.from(new Map(willSolveEvents.map((e) => [e.resource.tagCode, e])).values());

  const allTags = [...uniqueSolved, ...uniqueWillSolve];
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
