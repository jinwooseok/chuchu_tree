import { RecommendationApi } from '@/entities/recommendation/api/recommendation.api';
import { BanProblem } from '@/entities/recommendation/model/types';
import { UseMutationCallback } from '@/shared/types/api';
import { useMutation } from '@tanstack/react-query';

export const RecommendationKeys = {
  all: ['recommendation'],
  lists: () => [...RecommendationKeys.all, 'list'],
  list: (level: string, tags: string) => [...RecommendationKeys.lists(), { level, tags }],
};

export const useGetRecommendation = (callbacks?: UseMutationCallback) => {
  return useMutation({
    mutationFn: ({ level, tags }: { level: string; tags: string }) => RecommendationApi.getRecommendation({ level, tags }),
    onSuccess: () => {
      if (callbacks?.onSuccess) callbacks?.onSuccess();
    },
    onError: (error) => {
      if (callbacks?.onError) callbacks?.onError(error);
    },
  });
};

export const useBanProblem = (callbacks?: UseMutationCallback) => {
  return useMutation({
    mutationFn: (data: BanProblem) => RecommendationApi.postProblemBan(data),
    onSuccess: () => {
      if (callbacks?.onSuccess) callbacks?.onSuccess();
    },
    onError: (error) => {
      if (callbacks?.onError) callbacks?.onError(error);
    },
  });
};
