'use client';

import { useMutation, useQueryClient } from '@tanstack/react-query';
import { authApi } from '../api/auth.api';
import { UseMutationCallback } from '@/shared/types/api';
import '@/shared/types/query';

export const authKeys = {
  all: ['auth'],
  logout: () => [...authKeys.all, 'logout'],
};

export const useLogout = (callbacks?: UseMutationCallback) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: authApi.logout,
    onSuccess: () => {
      queryClient.clear();
      localStorage.clear();
      sessionStorage.clear();
      if (callbacks?.onSuccess) callbacks.onSuccess();
    },
    onError: (error) => {
      if (callbacks?.onError) callbacks.onError(error);
    },
  });
};
