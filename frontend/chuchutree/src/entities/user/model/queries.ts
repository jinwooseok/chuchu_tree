'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { userApi } from '../api/user.api';
import { PostTargetType } from './types';
import { UseMutationCallback } from '@/shared/types/api';
import { userKeys } from './keys';

export const useUser = () => {
  return useQuery({
    queryKey: userKeys.me(),
    queryFn: userApi.getMe,
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
