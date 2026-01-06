import { LinkBjAccountRequest } from '../model/types';
import { axiosInstance } from '@/lib/axios';

export const baekjoonApi = {
  linkAccount: async (data: LinkBjAccountRequest): Promise<void> => {
    await axiosInstance.post('bj-accounts/link', data);
  },
  patchAccount: async (data: LinkBjAccountRequest): Promise<void> => {
    await axiosInstance.patch('bj-accounts/link', data);
  },
};
