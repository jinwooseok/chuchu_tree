'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { userApi } from '../api/user.api';
import { PostTargetType } from './types';
import { UseMutationCallback } from '@/shared/types/api';

export const userKeys = {
  all: ['user'],
  me: () => [...userKeys.all, 'me'],
};

export const useUser = () => {
  return useQuery({
    queryKey: userKeys.me(),
    queryFn: userApi.getMe,
    staleTime: 5 * 60 * 1000,
  });
};

export const usePostTarget = (callbacks?: UseMutationCallback) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: PostTargetType) => userApi.postTarget(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: userKeys.me() });
      if (callbacks?.onSuccess) callbacks.onSuccess();
    },
    onError: (error) => {
      if (callbacks?.onError) callbacks.onError(error);
    },
  });
};
