import { RecommendationApi } from '@/entities/recommendation/api/recommendation.api';
import { useMutation } from '@tanstack/react-query';

export const RecommendationKeys = {
  all: ['recommendation'],
  lists: () => [...RecommendationKeys.all, 'list'],
  list: (level: string, tags: string) => [...RecommendationKeys.lists(), { level, tags }],
};

export const useGetRecommendation = () => {
  return useMutation({
    mutationFn: ({ level, tags }: { level: string; tags: string }) =>
      RecommendationApi.getRecommendation({ level, tags }),
  });
};
