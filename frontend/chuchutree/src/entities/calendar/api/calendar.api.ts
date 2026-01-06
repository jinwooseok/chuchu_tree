import { ApiResponse } from '@/shared/types/api';
import { Calendar } from '../model/types';
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
};
