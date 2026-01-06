import { ApiResponse } from '@/shared/types/api';
import { Calendar, UpdateProblemsData } from '../model/types';
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
};
