import { Calendar, MonthlyData } from '@/entities/calendar';
import calendarData1 from '../mock/bj-accounts_me_problems_25_12_260126.json';
import calendarData2 from '../mock/bj-accounts_me_problems_26_01_260126.json';
import calendarData3 from '../mock/bj-accounts_me_problems_26_02_260126.json';

// 빈 Calendar 데이터를 생성하는 헬퍼 함수
function createEmptyCalendar(year: number, month: number): Calendar {
  const daysInMonth = new Date(year, month, 0).getDate();
  const monthlyData: MonthlyData[] = [];

  for (let day = 1; day <= daysInMonth; day++) {
    const dateStr = `${year}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
    monthlyData.push({
      targetDate: dateStr,
      solvedProblemCount: 0,
      willSolveProblemCount: 0,
      solvedProblems: [],
      willSolveProblems: [],
    });
  }

  return {
    totalProblemCount: 0,
    monthlyData,
  };
}

export function useLandingCalendar({ year, month }: { year: number; month: number }): Calendar {
  // 2025년 12월 데이터
  if (year === 2025 && month === 12) {
    return calendarData1.data as Calendar;
  }

  // 2026년 1월 데이터
  if (year === 2026 && month === 1) {
    return calendarData2.data as Calendar;
  }

  // 2026년 2월 데이터
  if (year === 2026 && month === 2) {
    return calendarData3.data as Calendar;
  }

  // 해당하지 않는 경우 빈 Calendar 데이터 생성
  return createEmptyCalendar(year, month);
}
