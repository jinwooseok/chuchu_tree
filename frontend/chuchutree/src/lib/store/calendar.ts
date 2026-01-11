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

type State = {
  selectedDate: Date | null;
  bigCalendarDate: Date | null;
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
  bigCalendarDate: null,
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

          // BigCalendar 표시 월 설정
          setBigCalendarDate: (date: Date) => {
            set((state) => {
              state.bigCalendarDate = date;
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
  const selectedDate = calendarStoreInternal((s) => s.selectedDate);
  const bigCalendarDate = calendarStoreInternal((s) => s.bigCalendarDate);
  const monthlyData = calendarStoreInternal((s) => s.monthlyData);
  const totalProblemCount = calendarStoreInternal((s) => s.totalProblemCount);
  const isInitialized = calendarStoreInternal((s) => s.isInitialized);
  const getDataByDate = calendarStoreInternal((s) => s.getDataByDate);
  const getSolvedProblemsByDate = calendarStoreInternal((s) => s.getSolvedProblemsByDate);
  const getWillSolveProblemsByDate = calendarStoreInternal((s) => s.getWillSolveProblemsByDate);

  // actions는 별도로 가져오기 (stable reference)
  const setSelectedDate = calendarStoreInternal((s) => s.actions.setSelectedDate);
  const setCalendarData = calendarStoreInternal((s) => s.actions.setCalendarData);
  const setBigCalendarDate = calendarStoreInternal((s) => s.actions.setBigCalendarDate);
  const clearCalendarData = calendarStoreInternal((s) => s.actions.clearCalendarData);

  return {
    selectedDate,
    bigCalendarDate,
    monthlyData,
    totalProblemCount,
    isInitialized,
    actions: {
      setSelectedDate,
      setCalendarData,
      setBigCalendarDate,
      clearCalendarData,
    },
    getDataByDate,
    getSolvedProblemsByDate,
    getWillSolveProblemsByDate,
  };
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
