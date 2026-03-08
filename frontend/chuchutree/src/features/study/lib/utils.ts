import { CalendarEvent } from '@/entities/calendar';
import { StudyProblem, StudyMonthlyData } from '@/entities/study';

/**
 * 스터디 문제의 solved/willSolve 상태를 solveInfo 기반으로 판별
 * - 모든 멤버의 solved === true → 'solved'
 * - 한 명이라도 solved === false (또는 solveInfo가 빈 배열) → 'willSolve'
 */
export function getStudyProblemStatus(problem: StudyProblem): 'solved' | 'willSolve' {
  if (problem.solveInfo.length === 0) return 'willSolve';
  return problem.solveInfo.every((info) => info.solved) ? 'solved' : 'willSolve';
}

/**
 * StudyMonthlyData 배열을 react-big-calendar 이벤트 형식으로 변환
 * - 각 문제의 type은 getStudyProblemStatus()로 결정
 * - tag 없는 문제는 이벤트에서 제외 (기존 calendar 패턴 동일)
 */
export function transformToStudyCalendarEvents(monthlyDataArray: StudyMonthlyData[]): CalendarEvent[] {
  const events: CalendarEvent[] = [];

  monthlyDataArray.forEach((dayData) => {
    const date = new Date(dayData.targetDate);

    dayData.problems.forEach((problem) => {
      const lastTag = problem.tags.length > 0 ? problem.tags[problem.tags.length - 1] : null;
      const lastTagDisplayName = lastTag?.tagDisplayName ?? '';
      const lastTagCode = lastTag?.tagCode ?? '';

      if (!lastTag) return; // tag 없는 문제는 제외

      const type = getStudyProblemStatus(problem);

      events.push({
        title: problem.representativeTag?.tagDisplayName || lastTagDisplayName,
        start: date,
        end: date,
        resource: {
          type,
          problem: {
            problemId: problem.problemId,
            problemTitle: problem.problemTitle,
            problemTierLevel: problem.problemTierLevel,
            problemTierName: problem.problemTierName,
            problemClassLevel: problem.problemClassLevel,
            tags: problem.tags,
            representativeTag: problem.representativeTag,
          },
          tagCode: problem.representativeTag?.tagCode || lastTagCode,
        },
      });
    });
  });

  return events;
}
