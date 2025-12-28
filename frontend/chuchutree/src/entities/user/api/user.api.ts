import { ApiResponse } from '@/shared/types/api';
import { User } from '../model/types';
import { axiosInstance } from '@/lib/axios';

export const userApi = {
  getMe: async (): Promise<User> => {
    const { data } = await axiosInstance.get<ApiResponse<User>>('/api/user');
    return data.data;
  },

  getUserById: async (id: string): Promise<User> => {
    const { data } = await axiosInstance.get<ApiResponse<User>>(`/api/user/${id}`);
    return data.data;
  },
};
