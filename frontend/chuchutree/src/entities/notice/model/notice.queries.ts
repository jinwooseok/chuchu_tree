'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { noticeApi } from '../api/notice.api';
import { noticeKeys } from './notice.keys';

export const useNotices = () => {
  return useQuery({
    queryKey: noticeKeys.list(),
    queryFn: noticeApi.getNotices,
    staleTime: 0,
  });
};

export const useReadNotices = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (noticeIds: number[]) => noticeApi.readNotices(noticeIds),
    onSuccess: (_, noticeIds) => {
      queryClient.setQueryData(noticeKeys.list(), (prev: ReturnType<typeof useNotices>['data']) => {
        if (!prev) return prev;
        return prev.map((n) => (noticeIds.includes(n.noticeId) ? { ...n, isRead: true } : n));
      });
    },
  });
};
