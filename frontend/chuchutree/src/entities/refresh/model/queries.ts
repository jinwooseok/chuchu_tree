'use client';

import { refreshApi } from '@/entities/refresh/api/refresh.api';
import { UseMutationCallback } from '@/shared/types/api';
import { useMutation, useQueryClient } from '@tanstack/react-query';

export const useRefresh = (callbacks: UseMutationCallback) => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: refreshApi.getRefresh,
    onSuccess: () => {
      if (callbacks.onSuccess) callbacks.onSuccess();
      queryClient.invalidateQueries({ queryKey: ['user'] });
      queryClient.invalidateQueries({ queryKey: ['calendar'] });
      queryClient.invalidateQueries({ queryKey: ['tagDashboard'] });
    },
    onError: (error) => {
      if (callbacks.onError) callbacks.onError(error);
    },
  });
};
