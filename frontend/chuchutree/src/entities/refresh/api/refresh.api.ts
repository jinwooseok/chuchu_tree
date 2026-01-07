import { ApiResponse } from '@/shared/types/api';
import { axiosInstance } from '@/lib/axios';

export const refreshApi = {
  getRefresh: async (): Promise<void> => {
    const { data } = await axiosInstance.post<ApiResponse<void>>('/bj-accounts/me/refresh');
    return data.data;
  },
};
