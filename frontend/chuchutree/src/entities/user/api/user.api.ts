import { ApiResponse } from '@/shared/types/api';
import { User } from '../model/types';
import { axiosInstance } from '@/lib/axios';

export const userApi = {
  getMe: async (): Promise<User> => {
    const { data } = await axiosInstance.get<ApiResponse<User>>('bj-accounts/me');
    return data.data;
  },
};
