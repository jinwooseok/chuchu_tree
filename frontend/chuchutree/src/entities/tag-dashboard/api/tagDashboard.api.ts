import { axiosInstance } from '@/lib/axios';
import { TagBan, TagDashboard } from '../model/tagDashboard.types';
import { ApiResponse } from '@/shared/types/api';

export const tagDashboardApi = {
  getTagDashboard: async (): Promise<TagDashboard> => {
    const { data } = await axiosInstance.get<ApiResponse<TagDashboard>>('user-accounts/me/tags');
    return data.data;
  },
  postTagBan: async (data: { tagCode: TagBan }): Promise<void> => {
    await axiosInstance.post('user-accounts/me/tags/banned-list', data);
  },
  deleteTagBan: async ({ tagCode }: TagBan): Promise<void> => {
    await axiosInstance.delete('user-accounts/me/tags/banned-list', {
      params: {
        tagCode,
      },
    });
  },
};
