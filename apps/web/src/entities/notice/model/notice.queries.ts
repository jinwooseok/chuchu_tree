'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { noticeApi } from '../api/notice.api';
import { noticeKeys } from './notice.keys';
import { BaseNotice } from './notice.types';

export const useNotices = (options?: { enabled?: boolean }) => {
  return useQuery({
    queryKey: noticeKeys.list(),
    queryFn: noticeApi.getNotices,
    staleTime: 0,
    enabled: options?.enabled ?? true,
  });
};

export const useReadNotices = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (noticeIds: number[]) => noticeApi.readNotices(noticeIds),
    onSuccess: (_, noticeIds) => {
      queryClient.setQueryData<BaseNotice[]>(noticeKeys.list(), (prev) => {
        if (!prev) return prev;
        return prev.map((n) => (noticeIds.includes(n.noticeId) ? { ...n, isRead: true } : n));
      });
    },
  });
};
