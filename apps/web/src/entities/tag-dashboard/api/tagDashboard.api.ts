import { axiosInstance } from '@/lib/axios';
import { TagBan, TagDashboard, TagDetail } from '../model/tagDashboard.types';
import { ApiResponse } from '@/shared/types/api';
import { TagKey } from '@/shared/constants/tagSystem';

export const tagDashboardApi = {
  getTagDashboard: async (): Promise<TagDashboard> => {
    const { data } = await axiosInstance.get<ApiResponse<TagDashboard>>('user-accounts/me/tags');
    return data.data;
  },
  postTagBan: async (data: TagBan): Promise<void> => {
    await axiosInstance.post('user-accounts/me/tags/banned-list', data);
  },
  deleteTagBan: async ({ tagCode }: TagBan): Promise<void> => {
    await axiosInstance.delete('user-accounts/me/tags/banned-list', {
      params: {
        tagCode,
      },
    });
  },
  getTagDetail: async ({ code }: { code: TagKey }): Promise<TagDetail> => {
    const { data } = await axiosInstance.get<ApiResponse<TagDetail>>('user-accounts/me/tags/problems', {
      params: {
        code,
      },
    });
    return data.data;
  },
};
