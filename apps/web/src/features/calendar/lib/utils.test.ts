/**
 * 캘린더 유틸리티 함수 테스트
 */

import { CalendarEvent, MonthlyData } from '@/entities/calendar';
import { transformToCalendarEvents, getDisplayTags } from './utils';

describe('transformToCalendarEvents', () => {
  it('빈 배열을 처리한다', () => {
    const result = transformToCalendarEvents([]);
    expect(result).toEqual([]);
  });

  it('MonthlyData 배열을 CalendarEvent 배열로 변환한다', () => {
    const monthlyData: MonthlyData[] = [
      {
        targetDate: '2024-01-15',
        solvedProblemCount: 1,
        willSolveProblemCount: 0,
        solvedProblems: [
          {
            problemId: 1000,
            realSolvedYn: true,
            problemTitle: '테스트 문제',
            problemTierLevel: 10,
            problemTierName: 'S2',
            problemClassLevel: null,
            tags: [
              {
                tagId: 1,
                tagCode: 'greedy',
                tagDisplayName: '그리디',
                tagTargets: [],
                tagAliases: [],
              },
            ],
            representativeTag: {
              tagId: 1,
              tagCode: 'greedy',
              tagDisplayName: '그리디',
            },
          },
        ],
        willSolveProblems: [],
      },
    ];

    const result = transformToCalendarEvents(monthlyData);

    expect(result).toHaveLength(1);
    expect(result[0]).toMatchObject({
      title: '그리디',
      start: new Date('2024-01-15'),
      end: new Date('2024-01-15'),
      resource: {
        type: 'solved',
        tagCode: 'greedy',
      },
    });
  });

  it('solved 문제들을 이벤트로 변환한다', () => {
    const monthlyData: MonthlyData[] = [
      {
        targetDate: '2024-01-15',
        solvedProblemCount: 2,
        willSolveProblemCount: 0,
        solvedProblems: [
          {
            problemId: 1000,
            realSolvedYn: true,
            problemTitle: '문제1',
            problemTierLevel: 10,
            problemTierName: 'S2',
            problemClassLevel: null,
            tags: [
              {
                tagId: 1,
                tagCode: 'greedy',
                tagDisplayName: '그리디',
                tagTargets: [],
                tagAliases: [],
              },
            ],
            representativeTag: {
              tagId: 1,
              tagCode: 'greedy',
              tagDisplayName: '그리디',
            },
          },
          {
            problemId: 1001,
            realSolvedYn: true,
            problemTitle: '문제2',
            problemTierLevel: 12,
            problemTierName: 'G2',
            problemClassLevel: null,
            tags: [
              {
                tagId: 2,
                tagCode: 'dp',
                tagDisplayName: 'DP',
                tagTargets: [],
                tagAliases: [],
              },
            ],
            representativeTag: {
              tagId: 2,
              tagCode: 'dp',
              tagDisplayName: 'DP',
            },
          },
        ],
        willSolveProblems: [],
      },
    ];

    const result = transformToCalendarEvents(monthlyData);

    expect(result).toHaveLength(2);
    expect(result[0].resource.type).toBe('solved');
    expect(result[1].resource.type).toBe('solved');
  });

  it('willSolve 문제들을 이벤트로 변환한다', () => {
    const monthlyData: MonthlyData[] = [
      {
        targetDate: '2024-01-15',
        solvedProblemCount: 0,
        willSolveProblemCount: 1,
        solvedProblems: [],
        willSolveProblems: [
          {
            problemId: 2000,
            problemTitle: '풀 예정 문제',
            problemTierLevel: 10,
            problemTierName: 'S2',
            problemClassLevel: null,
            tags: [
              {
                tagId: 3,
                tagCode: 'implementation',
                tagDisplayName: '구현',
                tagTargets: [],
                tagAliases: [],
              },
            ],
            representativeTag: {
              tagId: 3,
              tagCode: 'implementation',
              tagDisplayName: '구현',
            },
          },
        ],
      },
    ];

    const result = transformToCalendarEvents(monthlyData);

    expect(result).toHaveLength(1);
    expect(result[0].resource.type).toBe('willSolve');
    expect(result[0].title).toBe('구현');
  });

  it('태그가 없는 solved 문제는 제외한다', () => {
    const monthlyData: MonthlyData[] = [
      {
        targetDate: '2024-01-15',
        solvedProblemCount: 1,
        willSolveProblemCount: 0,
        solvedProblems: [
          {
            problemId: 1000,
            realSolvedYn: true,
            problemTitle: '태그 없는 문제',
            problemTierLevel: 10,
            problemTierName: 'S2',
            problemClassLevel: null,
            tags: [],
            representativeTag: null,
          },
        ],
        willSolveProblems: [],
      },
    ];

    const result = transformToCalendarEvents(monthlyData);

    expect(result).toHaveLength(0);
  });

  it('태그가 없는 willSolve 문제는 제외한다', () => {
    const monthlyData: MonthlyData[] = [
      {
        targetDate: '2024-01-15',
        solvedProblemCount: 0,
        willSolveProblemCount: 1,
        solvedProblems: [],
        willSolveProblems: [
          {
            problemId: 2000,
            problemTitle: '태그 없는 willSolve 문제',
            problemTierLevel: 10,
            problemTierName: 'S2',
            problemClassLevel: null,
            tags: [],
            representativeTag: null,
          },
        ],
      },
    ];

    const result = transformToCalendarEvents(monthlyData);

    expect(result).toHaveLength(0);
  });

  it('representativeTag가 없으면 마지막 태그를 사용한다', () => {
    const monthlyData: MonthlyData[] = [
      {
        targetDate: '2024-01-15',
        solvedProblemCount: 1,
        willSolveProblemCount: 0,
        solvedProblems: [
          {
            problemId: 1000,
            realSolvedYn: true,
            problemTitle: '문제',
            problemTierLevel: 10,
            problemTierName: 'S2',
            problemClassLevel: null,
            tags: [
              {
                tagId: 1,
                tagCode: 'greedy',
                tagDisplayName: '그리디',
                tagTargets: [],
                tagAliases: [],
              },
              {
                tagId: 2,
                tagCode: 'dp',
                tagDisplayName: 'DP',
                tagTargets: [],
                tagAliases: [],
              },
            ],
            representativeTag: null,
          },
        ],
        willSolveProblems: [],
      },
    ];

    const result = transformToCalendarEvents(monthlyData);

    expect(result).toHaveLength(1);
    expect(result[0].title).toBe('DP'); // 마지막 태그
    expect(result[0].resource.tagCode).toBe('dp');
  });

  it('여러 날짜의 데이터를 처리한다', () => {
    const monthlyData: MonthlyData[] = [
      {
        targetDate: '2024-01-15',
        solvedProblemCount: 1,
        willSolveProblemCount: 0,
        solvedProblems: [
          {
            problemId: 1000,
            realSolvedYn: true,
            problemTitle: '문제1',
            problemTierLevel: 10,
            problemTierName: 'S2',
            problemClassLevel: null,
            tags: [
              {
                tagId: 1,
                tagCode: 'greedy',
                tagDisplayName: '그리디',
                tagTargets: [],
                tagAliases: [],
              },
            ],
            representativeTag: {
              tagId: 1,
              tagCode: 'greedy',
              tagDisplayName: '그리디',
            },
          },
        ],
        willSolveProblems: [],
      },
      {
        targetDate: '2024-01-16',
        solvedProblemCount: 1,
        willSolveProblemCount: 0,
        solvedProblems: [
          {
            problemId: 1001,
            realSolvedYn: true,
            problemTitle: '문제2',
            problemTierLevel: 12,
            problemTierName: 'G2',
            problemClassLevel: null,
            tags: [
              {
                tagId: 2,
                tagCode: 'dp',
                tagDisplayName: 'DP',
                tagTargets: [],
                tagAliases: [],
              },
            ],
            representativeTag: {
              tagId: 2,
              tagCode: 'dp',
              tagDisplayName: 'DP',
            },
          },
        ],
        willSolveProblems: [],
      },
    ];

    const result = transformToCalendarEvents(monthlyData);

    expect(result).toHaveLength(2);
    expect(result[0].start).toEqual(new Date('2024-01-15'));
    expect(result[1].start).toEqual(new Date('2024-01-16'));
  });

  it('willSolve 문제에서 representativeTag가 없으면 마지막 태그를 사용한다', () => {
    const monthlyData: MonthlyData[] = [
      {
        targetDate: '2024-01-15',
        solvedProblemCount: 0,
        willSolveProblemCount: 1,
        solvedProblems: [],
        willSolveProblems: [
          {
            problemId: 2000,
            problemTitle: '풀 예정 문제',
            problemTierLevel: 10,
            problemTierName: 'S2',
            problemClassLevel: null,
            tags: [
              {
                tagId: 1,
                tagCode: 'greedy',
                tagDisplayName: '그리디',
                tagTargets: [],
                tagAliases: [],
              },
              {
                tagId: 2,
                tagCode: 'string',
                tagDisplayName: '문자열',
                tagTargets: [],
                tagAliases: [],
              },
            ],
            representativeTag: null,
          },
        ],
      },
    ];

    const result = transformToCalendarEvents(monthlyData);

    expect(result).toHaveLength(1);
    expect(result[0].title).toBe('문자열'); // 마지막 태그
    expect(result[0].resource.tagCode).toBe('string');
    expect(result[0].resource.type).toBe('willSolve');
  });

  it('solved와 willSolve를 함께 처리한다', () => {
    const monthlyData: MonthlyData[] = [
      {
        targetDate: '2024-01-15',
        solvedProblemCount: 1,
        willSolveProblemCount: 1,
        solvedProblems: [
          {
            problemId: 1000,
            realSolvedYn: true,
            problemTitle: 'solved 문제',
            problemTierLevel: 10,
            problemTierName: 'S2',
            problemClassLevel: null,
            tags: [
              {
                tagId: 1,
                tagCode: 'greedy',
                tagDisplayName: '그리디',
                tagTargets: [],
                tagAliases: [],
              },
            ],
            representativeTag: {
              tagId: 1,
              tagCode: 'greedy',
              tagDisplayName: '그리디',
            },
          },
        ],
        willSolveProblems: [
          {
            problemId: 2000,
            problemTitle: 'willSolve 문제',
            problemTierLevel: 12,
            problemTierName: 'G2',
            problemClassLevel: null,
            tags: [
              {
                tagId: 2,
                tagCode: 'dp',
                tagDisplayName: 'DP',
                tagTargets: [],
                tagAliases: [],
              },
            ],
            representativeTag: {
              tagId: 2,
              tagCode: 'dp',
              tagDisplayName: 'DP',
            },
          },
        ],
      },
    ];

    const result = transformToCalendarEvents(monthlyData);

    expect(result).toHaveLength(2);
    expect(result[0].resource.type).toBe('solved');
    expect(result[1].resource.type).toBe('willSolve');
  });
});

describe('getDisplayTags', () => {
  const createMockEvent = (type: 'solved' | 'willSolve', tagCode: string): CalendarEvent => ({
    title: tagCode,
    start: new Date('2024-01-15'),
    end: new Date('2024-01-15'),
    resource: {
      type,
      problem: {} as any,
      tagCode,
    },
  });

  it('빈 배열을 처리한다', () => {
    const result = getDisplayTags([]);
    expect(result).toEqual({
      displayTags: [],
      hasMore: false,
      moreCount: 0,
    });
  });

  it('3개 이하의 태그는 모두 표시한다', () => {
    const events = [createMockEvent('solved', 'greedy'), createMockEvent('solved', 'dp'), createMockEvent('solved', 'implementation')];

    const result = getDisplayTags(events);

    expect(result.displayTags).toHaveLength(3);
    expect(result.hasMore).toBe(false);
    expect(result.moreCount).toBe(0);
  });

  it('4개 이상의 태그는 2개만 표시하고 나머지는 "n개 더보기"', () => {
    const events = [createMockEvent('solved', 'greedy'), createMockEvent('solved', 'dp'), createMockEvent('solved', 'implementation'), createMockEvent('solved', 'graph')];

    const result = getDisplayTags(events);

    expect(result.displayTags).toHaveLength(2);
    expect(result.hasMore).toBe(true);
    expect(result.moreCount).toBe(2);
  });

  it('solved 문제를 우선순위로 표시한다', () => {
    const events = [createMockEvent('willSolve', 'greedy'), createMockEvent('solved', 'dp'), createMockEvent('willSolve', 'implementation'), createMockEvent('solved', 'graph')];

    const result = getDisplayTags(events);

    // solved 문제가 앞에 오는지 확인
    expect(result.displayTags[0].resource.type).toBe('solved');
    expect(result.displayTags[1].resource.type).toBe('solved');
  });

  it('정확히 3개의 태그는 모두 표시한다', () => {
    const events = [createMockEvent('solved', 'greedy'), createMockEvent('solved', 'dp'), createMockEvent('solved', 'implementation')];

    const result = getDisplayTags(events);

    expect(result.displayTags).toHaveLength(3);
    expect(result.hasMore).toBe(false);
    expect(result.moreCount).toBe(0);
  });

  it('5개 이상의 태그도 2개만 표시한다', () => {
    const events = [
      createMockEvent('solved', 'greedy'),
      createMockEvent('solved', 'dp'),
      createMockEvent('solved', 'implementation'),
      createMockEvent('solved', 'graph'),
      createMockEvent('solved', 'string'),
    ];

    const result = getDisplayTags(events);

    expect(result.displayTags).toHaveLength(2);
    expect(result.hasMore).toBe(true);
    expect(result.moreCount).toBe(3);
  });

  it('1개의 태그는 그대로 표시한다', () => {
    const events = [createMockEvent('solved', 'greedy')];

    const result = getDisplayTags(events);

    expect(result.displayTags).toHaveLength(1);
    expect(result.hasMore).toBe(false);
    expect(result.moreCount).toBe(0);
  });
});
