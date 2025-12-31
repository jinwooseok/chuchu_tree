import { create } from 'zustand';
import { MonthlyData, Problem } from '@/shared/types/calendar';
import mockData from '@/features/calendar/mockdata/mock_calendar_data.json';

interface CalendarStore {
  // 상태
  selectedDate: Date;
  monthlyData: MonthlyData[];

  // 액션
  setSelectedDate: (date: Date) => void;

  // 셀렉터 (특정 날짜의 데이터 가져오기)
  getDataByDate: (date: Date) => MonthlyData | undefined;
  getSolvedProblemsByDate: (date: Date) => Problem[];
  getWillSolveProblemsByDate: (date: Date) => Problem[];

  // 문제 추가/삭제 (향후 구현)
  addProblemToWillSolve: (date: Date, problem: Problem) => void;
  removeProblemFromWillSolve: (date: Date, problemId: number) => void;
}

// 날짜를 YYYY-MM-DD 형식 문자열로 변환
const formatDateString = (date: Date): string => {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
};

export const useCalendarStore = create<CalendarStore>((set, get) => ({
  // 초기 상태
  selectedDate: new Date(),
  monthlyData: mockData.data.monthlyData as MonthlyData[],

  // 날짜 선택
  setSelectedDate: (date: Date) => {
    set({ selectedDate: date });
  },

  // 특정 날짜의 전체 데이터 가져오기
  getDataByDate: (date: Date) => {
    const dateString = formatDateString(date);
    return get().monthlyData.find((data) => data.date === dateString);
  },

  // 특정 날짜의 solved 문제들 가져오기
  getSolvedProblemsByDate: (date: Date) => {
    const data = get().getDataByDate(date);
    return data?.solvedProblems || [];
  },

  // 특정 날짜의 will solve 문제들 가져오기
  getWillSolveProblemsByDate: (date: Date) => {
    const data = get().getDataByDate(date);
    return data?.willSolveProblem || [];
  },

  // will solve에 문제 추가 (임시 구현 - 나중에 API 연동 시 수정)
  addProblemToWillSolve: (date: Date, problem: Problem) => {
    const dateString = formatDateString(date);
    set((state) => ({
      monthlyData: state.monthlyData.map((data) => {
        if (data.date === dateString) {
          return {
            ...data,
            willSolveProblem: [...data.willSolveProblem, problem],
            willSolveProblemCount: data.willSolveProblemCount + 1,
          };
        }
        return data;
      }),
    }));
  },

  // will solve에서 문제 삭제 (임시 구현 - 나중에 API 연동 시 수정)
  removeProblemFromWillSolve: (date: Date, problemId: number) => {
    const dateString = formatDateString(date);
    set((state) => ({
      monthlyData: state.monthlyData.map((data) => {
        if (data.date === dateString) {
          return {
            ...data,
            willSolveProblem: data.willSolveProblem.filter((p) => p.problemId !== problemId),
            willSolveProblemCount: Math.max(0, data.willSolveProblemCount - 1),
          };
        }
        return data;
      }),
    }));
  },
}));
