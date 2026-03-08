'use client';

import { useInfiniteQuery, useMutation } from '@tanstack/react-query';
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

export const useGetStudyRecommendHistory = (studyId: number) => {
  return useInfiniteQuery({
    queryKey: ['study', studyId, 'recommend-history'],
    queryFn: ({ pageParam }) => studyRecommendationApi.getStudyRecommendHistory({ study_id: studyId, page: pageParam, size: 10 }),
    initialPageParam: 1,
    getNextPageParam: (lastPage, _, lastPageParam) => (lastPage.hasNext ? lastPageParam + 1 : undefined),
  });
};
