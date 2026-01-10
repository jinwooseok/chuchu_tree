'use client';

import { tagDashboardApi } from '../api/tagDashboard.api';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { TagBan } from './tagDashboard.types';
import { UseMutationCallback } from '@/shared/types/api';

export const tagDashboardKeys = {
  all: ['tagDashboard'] as const,
  dashboard: () => [...tagDashboardKeys.all, 'dashboard'] as const,
};

export const useTagDashboard = () => {
  return useQuery({
    queryKey: tagDashboardKeys.dashboard(),
    queryFn: () => tagDashboardApi.getTagDashboard(),
    staleTime: 5 * 60 * 1000,
  });
};

// Tag Ban 추가 mutation
export const usePostTagBan = (callbacks?: UseMutationCallback) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: TagBan) => tagDashboardApi.postTagBan(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: tagDashboardKeys.dashboard() });
      if (callbacks?.onSuccess) callbacks.onSuccess();
    },
    onError: (error) => {
      if (callbacks?.onError) callbacks.onError(error);
    },
  });
};

// Tag Ban 삭제 mutation
export const useDeleteTagBan = (callbacks?: UseMutationCallback) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: TagBan) => tagDashboardApi.deleteTagBan(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: tagDashboardKeys.dashboard() });
      if (callbacks?.onSuccess) callbacks.onSuccess();
    },
    onError: (error) => {
      if (callbacks?.onError) callbacks.onError(error);
    },
  });
};