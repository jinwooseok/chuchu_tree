import { ApiResponse } from '@/shared/types/api';
import { StudyRecommendationResponse, StudyRecommendParams } from '../model/study-recommendation.types';
import { axiosInstance } from '@/lib/axios';

export const studyRecommendationApi = {
  getStudyRecommendation: async (params: StudyRecommendParams): Promise<StudyRecommendationResponse> => {
    const { study_id, ...rest } = params;
    const { data } = await axiosInstance.get<ApiResponse<StudyRecommendationResponse>>(`/studies/${study_id}/recommend-problems`, {
      params: rest,
    });
    return data.data;
  },
};
