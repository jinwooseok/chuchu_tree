import { Calendar, MonthlyData, SolvedProblems, WillSolveProblems } from '@/entities/calendar';
import seedData from '../mock/seed_problems_source.json';

// 시드 데이터의 문제 타입
interface SeedProblem {
  problemId: number;
  problemTitle: string;
  problemTierLevel: number;
  problemTierName: string;
  problemClassLevel: number | null;
  tags: {
    tagId: number;
    tagCode: string;
    tagDisplayName: string;
  }[];
}

// 결정론적 랜덤 생성기 (year, month, day를 시드로 사용)
function createSeededRandom(year: number, month: number, day: number = 1) {
  let seed = year * 10000 + month * 100 + day;
  return () => {
    seed = (seed * 9301 + 49297) % 233280;
    return seed / 233280;
  };
}

// 시드 문제를 SolvedProblems 타입으로 변환
function toSolvedProblem(seedProblem: SeedProblem): SolvedProblems {
  return {
    problemId: seedProblem.problemId,
    problemTitle: seedProblem.problemTitle,
    problemTierLevel: seedProblem.problemTierLevel as any,
    problemTierName: seedProblem.problemTierName as any,
    problemClassLevel: seedProblem.problemClassLevel,
    realSolvedYn: false,
    tags: seedProblem.tags.map((tag) => ({
      tagId: tag.tagId,
      tagCode: tag.tagCode as any,
      tagDisplayName: tag.tagDisplayName,
      tagTargets: [],
      tagAliases: [],
    })),
    representativeTag: null,
  };
}

// 시드 문제를 WillSolveProblems 타입으로 변환
function toWillSolveProblem(seedProblem: SeedProblem): WillSolveProblems {
  return {
    problemId: seedProblem.problemId,
    problemTitle: seedProblem.problemTitle,
    problemTierLevel: seedProblem.problemTierLevel as any,
    problemTierName: seedProblem.problemTierName as any,
    problemClassLevel: seedProblem.problemClassLevel,
    tags: seedProblem.tags.map((tag) => ({
      tagId: tag.tagId,
      tagCode: tag.tagCode as any,
      tagDisplayName: tag.tagDisplayName,
      tagTargets: [],
      tagAliases: [],
    })),
    representativeTag: null,
  };
}

// 배열을 섞는 함수 (Fisher-Yates shuffle with seeded random)
function shuffleArray<T>(array: T[], random: () => number): T[] {
  const shuffled = [...array];
  for (let i = shuffled.length - 1; i > 0; i--) {
    const j = Math.floor(random() * (i + 1));
    [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
  }
  return shuffled;
}

// 동적으로 Calendar 데이터 생성
function generateCalendar(year: number, month: number): Calendar {
  const today = new Date();
  today.setHours(0, 0, 0, 0); // 시간 제거

  const daysInMonth = new Date(year, month, 0).getDate();
  const monthlyData: MonthlyData[] = [];

  // 시드 문제 풀에서 섞인 문제 리스트 생성
  const random = createSeededRandom(year, month);
  const problems = seedData.data.problems as SeedProblem[];
  const shuffledProblems = shuffleArray(problems, random);

  // 사용된 문제 ID 추적 (같은 달 내 중복 방지)
  const usedProblemIds = new Set<number>();
  let problemIndex = 0;

  // 문제 선택 헬퍼 함수 (for 루프 밖에서 정의하여 전체에서 사용 가능)
  const pickProblems = (count: number): SeedProblem[] => {
    const picked: SeedProblem[] = [];
    let attempts = 0;
    const maxAttempts = problems.length * 2;

    while (picked.length < count && attempts < maxAttempts) {
      const problem = shuffledProblems[problemIndex % shuffledProblems.length];
      problemIndex++;
      attempts++;

      if (!usedProblemIds.has(problem.problemId)) {
        picked.push(problem);
        usedProblemIds.add(problem.problemId);
      }
    }

    return picked;
  };

  // 각 날짜별로 문제 배치
  for (let day = 1; day <= daysInMonth; day++) {
    const targetDate = new Date(year, month - 1, day);
    targetDate.setHours(0, 0, 0, 0);
    const dateStr = `${year}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}`;

    // 날짜별 랜덤 생성기
    const dayRandom = createSeededRandom(year, month, day);

    const dayData: MonthlyData = {
      targetDate: dateStr,
      solvedProblemCount: 0,
      willSolveProblemCount: 0,
      solvedProblems: [],
      willSolveProblems: [],
    };

    const diffDays = Math.floor((targetDate.getTime() - today.getTime()) / (1000 * 60 * 60 * 24));

    if (diffDays === 0) {
      // 오늘: solved 1개, willSolve 2개
      const solvedCount = 1;
      const willSolveCount = 2;

      const solvedPicks = pickProblems(solvedCount);
      const willSolvePicks = pickProblems(willSolveCount);

      dayData.solvedProblems = solvedPicks.map(toSolvedProblem);
      dayData.willSolveProblems = willSolvePicks.map(toWillSolveProblem);
      dayData.solvedProblemCount = solvedPicks.length;
      dayData.willSolveProblemCount = willSolvePicks.length;
    } else if (diffDays < 0) {
      // 과거: solved 0-3개, willSolve 0-2개
      const solvedCount = Math.floor(dayRandom() * 4); // 0-3
      const willSolveCount = Math.floor(dayRandom() * 3); // 0-2

      const solvedPicks = pickProblems(solvedCount);
      const willSolvePicks = pickProblems(willSolveCount);

      dayData.solvedProblems = solvedPicks.map(toSolvedProblem);
      dayData.willSolveProblems = willSolvePicks.map(toWillSolveProblem);
      dayData.solvedProblemCount = solvedPicks.length;
      dayData.willSolveProblemCount = willSolvePicks.length;
    } else if (diffDays >= 1 && diffDays <= 7) {
      // 오늘+1일 ~ 오늘+7일: willSolve만 1-3개
      const willSolveCount = 1 + Math.floor(dayRandom() * 3); // 1-3

      const willSolvePicks = pickProblems(willSolveCount);

      dayData.willSolveProblems = willSolvePicks.map(toWillSolveProblem);
      dayData.willSolveProblemCount = willSolvePicks.length;
    } else if (diffDays >= 8 && diffDays <= 30) {
      // 오늘+8일 ~ 오늘+30일: willSolve만 0-1개
      const willSolveCount = Math.floor(dayRandom() * 2); // 0-1

      const willSolvePicks = pickProblems(willSolveCount);

      dayData.willSolveProblems = willSolvePicks.map(toWillSolveProblem);
      dayData.willSolveProblemCount = willSolvePicks.length;
    }
    // else: 오늘+31일 이후는 빈 배열 (이미 초기화됨)

    monthlyData.push(dayData);
  }

  // 총 문제 수 계산
  const totalProblemCount = monthlyData.reduce((sum, day) => sum + day.solvedProblemCount + day.willSolveProblemCount, 0);

  return {
    totalProblemCount,
    monthlyData,
  };
}

export function useLandingCalendar({ year, month }: { year: number; month: number }): Calendar {
  return generateCalendar(year, month);
}
