'use client';

import { refreshApi } from '@/entities/refresh/api/refresh.api';
import { useMutation, useQueryClient } from '@tanstack/react-query';

export const useRefresh = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: refreshApi.getRefresh,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['user'] });
      queryClient.invalidateQueries({ queryKey: ['calendar'] });
    },
  });
};
