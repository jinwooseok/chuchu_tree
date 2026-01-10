import { Recommendation } from '@/entities/recommendation/model/types';
import { axiosInstance } from '@/lib/axios';
import { ApiResponse } from '@/shared/types/api';

export const RecommendationApi = {
  getRecommendation: async ({ level, tags }: { level: string; tags: string }): Promise<Recommendation> => {
    const { data } = await axiosInstance.get<ApiResponse<Recommendation>>('/user-accounts/me/problems', {
      params: {
        level,
        tags,
      },
    });
    return data.data;
  },
};
