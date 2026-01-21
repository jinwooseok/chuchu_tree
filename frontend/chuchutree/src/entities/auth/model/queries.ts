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
      // Clear all query cache on logout
      queryClient.clear();
      // 특정 쿠키만 삭제 (accessToken, refreshToken 등)
      const cookiesToDelete = ['access_token', 'refresh_token'];
      cookiesToDelete.forEach((cookieName) => {
        document.cookie = `${cookieName}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;`;
      });
      // storage clear
      localStorage.clear();
      sessionStorage.clear();

      if (callbacks?.onSuccess) callbacks.onSuccess();
    },
    onError: (error) => {
      if (callbacks?.onError) callbacks.onError(error);
    },
  });
};
