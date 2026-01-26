import { ApiResponse } from '@/shared/types/api';
import { PostTargetType, Streak, User } from '../model/types';
import { axiosInstance } from '@/lib/axios';

export const userApi = {
  getMe: async (): Promise<User> => {
    const { data } = await axiosInstance.get<ApiResponse<User>>('bj-accounts/me');
    return data.data;
  },
  postTarget: async (data: PostTargetType): Promise<void> => {
    await axiosInstance.post('/user-accounts/me/targets', data);
  },
  getStreak: async ({ startDate, endDate }: { startDate: string; endDate: string }): Promise<Streak> => {
    const { data } = await axiosInstance.get<ApiResponse<Streak>>('bj-accounts/me/streak', {
      params: { startDate, endDate },
    });
    return data.data;
  },
};
