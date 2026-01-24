import { ApiResponse } from '@/shared/types/api';
import { Calendar, UpdateProblemsData, SearchProblems, BatchSolvedProblems } from '../model/calendar.types';
import { axiosInstance } from '@/lib/axios';

export const calendarApi = {
  getCalendar: async ({ year, month }: { year: number; month: number }): Promise<Calendar> => {
    const { data } = await axiosInstance.get<ApiResponse<Calendar>>('bj-accounts/me/problems', {
      params: {
        year,
        month,
      },
    });
    return data.data;
  },
  updateWillSolveProblems: async (data: UpdateProblemsData): Promise<void> => {
    await axiosInstance.post('/user-accounts/me/problems/will-solve-problems', data);
  },
  updateSolvedProblems: async (data: UpdateProblemsData): Promise<void> => {
    await axiosInstance.post('/user-accounts/me/problems/solved-problems', data);
  },
  getSearchProblems: async ({ keyword }: { keyword: string }): Promise<SearchProblems> => {
    const { data } = await axiosInstance.get<ApiResponse<SearchProblems>>('problems/search', {
      params: {
        keyword,
      },
    });
    return data.data;
  },
  updateRepresentativeTag: async ({ problemId, representativeTagCode }: { problemId: number; representativeTagCode: string }): Promise<void> => {
    await axiosInstance.put(`/user-accounts/me/problems/${problemId}/representative-tag`, {
      representativeTagCode,
    });
  },
  batchSolvedProblems: async (data: BatchSolvedProblems[]): Promise<void> => {
    await axiosInstance.post('/user-accounts/me/problems/solved-problems/batch', data);
  },
};
