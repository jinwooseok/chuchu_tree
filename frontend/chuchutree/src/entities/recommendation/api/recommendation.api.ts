import { BannedProblems, BanProblem, Recommendation } from '@/entities/recommendation/model/types';
import { axiosInstance } from '@/lib/axios';
import { ApiResponse } from '@/shared/types/api';

export const RecommendationApi = {
  getRecommendation: async ({ level, tags, count, exclusion_mode }: { level: string; tags: string; count: number; exclusion_mode: string }): Promise<Recommendation> => {
    const { data } = await axiosInstance.get<ApiResponse<Recommendation>>('/user-accounts/me/problems', {
      params: {
        level,
        tags,
        count,
        exclusion_mode,
      },
    });
    return data.data;
  },
  getBannedProblems: async (): Promise<BannedProblems> => {
    const { data } = await axiosInstance.get<ApiResponse<BannedProblems>>('/user-accounts/me/problems/banned-list');
    return data.data;
  },
  postProblemBan: async (data: BanProblem): Promise<void> => {
    await axiosInstance.post<void>('/user-accounts/me/problems/banned-list', data);
  },
  deleteProblemBan: async (data: BanProblem): Promise<void> => {
    await axiosInstance.delete<void>('/user-accounts/me/problems/banned-list', {
      params: {
        problemId: data.problemId,
      },
    });
  },
};
