'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { userApi } from '../api/user.api';
import { PostTargetType, User } from './types';
import { UseMutationCallback } from '@/shared/types/api';
import { streakKeys, userKeys } from './keys';
import '@/shared/types/query';

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

export const useSteaks = (startDate: string, endDate: string) => {
  return useQuery({
    queryKey: streakKeys.list(startDate, endDate),
    queryFn: () => userApi.getStreak({ startDate, endDate }),
  });
};

export const usePostProfileImage = (callbacks?: UseMutationCallback) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (file: File) => {
      const formData = new FormData();
      formData.append('profile_image', file);
      return userApi.postProfileImage(formData);
    },
    onMutate: async (file: File) => {
      await queryClient.cancelQueries({ queryKey: userKeys.me() });
      const previousUser = queryClient.getQueryData<User>(userKeys.me());
      const blobUrl = URL.createObjectURL(file);
      if (previousUser) {
        queryClient.setQueryData<User>(userKeys.me(), {
          ...previousUser,
          userAccount: { ...previousUser.userAccount, profileImageUrl: blobUrl },
        });
      }
      return { previousUser, blobUrl };
    },
    onSuccess: (data, _file, context) => {
      if (context?.blobUrl) URL.revokeObjectURL(context.blobUrl);
      const currentUser = queryClient.getQueryData<User>(userKeys.me());
      if (currentUser) {
        queryClient.setQueryData<User>(userKeys.me(), {
          ...currentUser,
          userAccount: { ...currentUser.userAccount, profileImageUrl: data.profileImageUrl },
        });
      }
      callbacks?.onSuccess?.();
    },
    onError: (error, _file, context) => {
      if (context?.blobUrl) URL.revokeObjectURL(context.blobUrl);
      if (context?.previousUser) {
        queryClient.setQueryData<User>(userKeys.me(), context.previousUser);
      }
      callbacks?.onError?.(error);
    },
  });
};

export const useDeleteProfileImage = (callbacks?: UseMutationCallback) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: userApi.deleteProfileImage,
    onMutate: async () => {
      await queryClient.cancelQueries({ queryKey: userKeys.me() });
      const previousUser = queryClient.getQueryData<User>(userKeys.me());
      if (previousUser) {
        queryClient.setQueryData<User>(userKeys.me(), {
          ...previousUser,
          userAccount: { ...previousUser.userAccount, profileImageUrl: null },
        });
      }
      return { previousUser };
    },
    onSuccess: () => {
      callbacks?.onSuccess?.();
    },
    onError: (error, _vars, context) => {
      if (context?.previousUser) {
        queryClient.setQueryData<User>(userKeys.me(), context.previousUser);
      }
      callbacks?.onError?.(error);
    },
  });
};
