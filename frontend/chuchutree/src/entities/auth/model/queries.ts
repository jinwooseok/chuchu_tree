'use client';

import { useMutation, useQueryClient } from '@tanstack/react-query';
import { authApi } from '../api/auth.api';
import { UseMutationCallback } from '@/shared/types/api';

export const authKeys = {
  all: ['auth'],
  logout: () => [...authKeys.all, 'logout'],
};

export const useLogout = (callbacks?: UseMutationCallback) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: authApi.logout,
    onSuccess: () => {
      // Clear all query cache on logout
      queryClient.clear();
      if (callbacks?.onSuccess) callbacks.onSuccess();
    },
    onError: (error) => {
      if (callbacks?.onError) callbacks.onError(error);
    },
  });
};
