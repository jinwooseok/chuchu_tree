import { RecommendationApi } from '@/entities/recommendation/api/recommendation.api';
import { BanProblem, Recommendation } from '@/entities/recommendation/model/types';
import { UseMutationCallback } from '@/shared/types/api';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import '@/shared/types/query';

export const RecommendationKeys = {
  all: ['recommendation'],
  lists: () => [...RecommendationKeys.all, 'list'],
  list: (level: string, tags: string) => [...RecommendationKeys.lists(), { level, tags }],
  bannedProblems: () => [...RecommendationKeys.all, 'banned'],
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

export const useGetBannedProblems = () => {
  return useQuery({
    queryKey: RecommendationKeys.bannedProblems(),
    queryFn: RecommendationApi.getBannedProblems,
  });
};

export const useBanProblem = (callbacks?: UseMutationCallback) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: BanProblem) => RecommendationApi.postProblemBan(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: RecommendationKeys.bannedProblems() });
      if (callbacks?.onSuccess) callbacks?.onSuccess();
    },
    onError: (error) => {
      if (callbacks?.onError) callbacks?.onError(error);
    },
  });
};

export const useUnbanProblem = (callbacks?: UseMutationCallback) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: BanProblem) => RecommendationApi.deleteProblemBan(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: RecommendationKeys.bannedProblems() });
      if (callbacks?.onSuccess) callbacks?.onSuccess();
    },
    onError: (error) => {
      if (callbacks?.onError) callbacks?.onError(error);
    },
  });
};
