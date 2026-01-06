import { create } from 'zustand';
import { combine, devtools } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';
import { Calendar } from '@/entities/calendar';

interface MonthlyData {
  targetDate: string;
  solvedProblemCount: number;
  willSolveProblemCount: number;
  solvedProblems: any[];
  willSolveProblems: any[];
}

interface Problem {
  problemId: number;
  problemTitle: string;
  problemTierLevel: number;
  problemTierName: string;
  problemClassLevel: number;
  tags: any[];
}

type State = {
  selectedDate: Date | null;
  monthlyData: MonthlyData[];
  totalProblemCount: number;
  isInitialized: boolean;
};

// 날짜를 YYYY-MM-DD 형식 문자열로 변환
const formatDateString = (date: Date): string => {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
};

const initialState: State = {
  selectedDate: null,
  monthlyData: [],
  totalProblemCount: 0,
  isInitialized: false,
};

const calendarStoreInternal = create(
  devtools(
    immer(
      combine(initialState, (set, get) => ({
        actions: {
          // Calendar 데이터 설정
          setCalendarData: (calendar: Calendar) => {
            set((state) => {
              state.monthlyData = calendar.monthlyData;
              state.totalProblemCount = calendar.totalProblemCount;
              state.isInitialized = true;
              // selectedDate가 없으면 오늘 날짜로 설정
              if (!state.selectedDate) {
                state.selectedDate = new Date();
              }
            });
          },

          // 선택된 날짜 설정
          setSelectedDate: (date: Date) => {
            set((state) => {
              state.selectedDate = date;
            });
          },

          // Calendar 데이터 초기화
          clearCalendarData: () => {
            set((state) => {
              state.selectedDate = null;
              state.monthlyData = [];
              state.totalProblemCount = 0;
              state.isInitialized = false;
            });
          },

          // will solve에 문제 추가 (향후 API 연동)
          addProblemToWillSolve: (date: Date, problem: Problem) => {
            const dateString = formatDateString(date);
            set((state) => {
              const dataIndex = state.monthlyData.findIndex((data) => data.targetDate === dateString);
              if (dataIndex !== -1) {
                state.monthlyData[dataIndex].willSolveProblems.push(problem);
                state.monthlyData[dataIndex].willSolveProblemCount += 1;
              }
            });
          },

          // will solve에서 문제 삭제 (향후 API 연동)
          removeProblemFromWillSolve: (date: Date, problemId: number) => {
            const dateString = formatDateString(date);
            set((state) => {
              const dataIndex = state.monthlyData.findIndex((data) => data.targetDate === dateString);
              if (dataIndex !== -1) {
                state.monthlyData[dataIndex].willSolveProblems = state.monthlyData[dataIndex].willSolveProblems.filter(
                  (p: Problem) => p.problemId !== problemId
                );
                state.monthlyData[dataIndex].willSolveProblemCount = Math.max(
                  0,
                  state.monthlyData[dataIndex].willSolveProblemCount - 1
                );
              }
            });
          },
        },

        // Selectors
        getDataByDate: (date: Date) => {
          const dateString = formatDateString(date);
          return get().monthlyData.find((data) => data.targetDate === dateString);
        },

        getSolvedProblemsByDate: (date: Date) => {
          const dateString = formatDateString(date);
          const data = get().monthlyData.find((data) => data.targetDate === dateString);
          return data?.solvedProblems || [];
        },

        getWillSolveProblemsByDate: (date: Date) => {
          const dateString = formatDateString(date);
          const data = get().monthlyData.find((data) => data.targetDate === dateString);
          return data?.willSolveProblems || [];
        },
      }))
    ),
    { name: 'CalendarStore' }
  )
);

// Selectors
export const useCalendarStore = () => {
  const store = calendarStoreInternal();
  return store as typeof store & State;
};

export const useSetCalendarData = () => {
  const setCalendarData = calendarStoreInternal((s) => s.actions.setCalendarData);
  return setCalendarData;
};

export const useSetSelectedDate = () => {
  const setSelectedDate = calendarStoreInternal((s) => s.actions.setSelectedDate);
  return setSelectedDate;
};

export const useClearCalendarData = () => {
  const clearCalendarData = calendarStoreInternal((s) => s.actions.clearCalendarData);
  return clearCalendarData;
};

export const useAddProblemToWillSolve = () => {
  const addProblemToWillSolve = calendarStoreInternal((s) => s.actions.addProblemToWillSolve);
  return addProblemToWillSolve;
};

export const useRemoveProblemFromWillSolve = () => {
  const removeProblemFromWillSolve = calendarStoreInternal((s) => s.actions.removeProblemFromWillSolve);
  return removeProblemFromWillSolve;
};
