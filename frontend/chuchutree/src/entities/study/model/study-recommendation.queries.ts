'use client';

import { useMutation } from '@tanstack/react-query';
import { studyRecommendationApi } from '../api/study-recommendation.api';
import { StudyRecommendParams } from './study-recommendation.types';
import { UseMutationCallback } from '@/shared/types/api';

export const useGetStudyRecommendation = (callbacks?: UseMutationCallback) => {
  return useMutation({
    mutationFn: (params: StudyRecommendParams) => studyRecommendationApi.getStudyRecommendation(params),
    onSuccess: () => callbacks?.onSuccess?.(),
    onError: (error) => callbacks?.onError?.(error),
  });
};
