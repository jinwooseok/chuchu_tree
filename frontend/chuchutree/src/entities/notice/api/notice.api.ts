import { ApiResponse } from '@/shared/types/api';
import { BaseNotice } from '../model/notice.types';
import { axiosInstance } from '@/lib/axios';

export const noticeApi = {
  getNotices: async (): Promise<BaseNotice[]> => {
    const { data } = await axiosInstance.get<ApiResponse<{ notices: BaseNotice[] }>>('/user-accounts/me/notices');
    return data.data.notices;
  },

  readNotices: async (noticeIds: number[]): Promise<void> => {
    await axiosInstance.patch('/user-accounts/me/notices/read', { noticeIds });
  },
};
