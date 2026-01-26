import { axiosInstance } from '@/lib/axios';

export const authApi = {
  logout: async (): Promise<void> => {
    await axiosInstance.post('auth/logout');
  },
};
