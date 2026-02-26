'use client';

import { tagDashboardApi } from '../api/tagDashboard.api';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { CategoryTags, TagBan, TagDashboard } from './tagDashboard.types';
import { UseMutationCallback } from '@/shared/types/api';
import { tagDashboardKeys } from './keys';
import { TagKey } from '@/shared/constants/tagSystem';
import '@/shared/types/query';

export const useTagDashboard = () => {
  return useQuery({
    queryKey: tagDashboardKeys.dashboard(),
    queryFn: () => tagDashboardApi.getTagDashboard(),
  });
};

// Tag Ban 추가 mutation
export const usePostTagBan = (callbacks?: UseMutationCallback) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: TagBan) => tagDashboardApi.postTagBan(data),
    onMutate: async (data) => {
      // 진행 중인 쿼리 취소하여 낙관적 업데이트가 덮어써지지 않도록 함
      await queryClient.cancelQueries({ queryKey: tagDashboardKeys.dashboard() });

      // 이전 데이터 백업 (롤백용)
      const previousData = queryClient.getQueryData(tagDashboardKeys.dashboard());

      // 낙관적으로 캐시 업데이트 (해당 태그만)
      queryClient.setQueryData(tagDashboardKeys.dashboard(), (old: TagDashboard) => {
        if (!old) return old;

        return {
          ...old,
          tags: old.tags.map((tag: CategoryTags) =>
            tag.tagCode === data.tagCode
              ? { ...tag, excludedYn: true, recommendationYn: false } // 추천 제외
              : tag,
          ),
        };
      });

      // context로 이전 데이터 반환
      return { previousData };
    },
    onError: (error, data, context) => {
      // 에러 발생 시 이전 데이터로 롤백
      if (context?.previousData) {
        queryClient.setQueryData(tagDashboardKeys.dashboard(), context.previousData);
      }
      if (callbacks?.onError) callbacks.onError(error);
    },
    onSuccess: () => {
      // invalidateQueries 제거 (낙관적 업데이트로 이미 반영됨)
      // 전체 리페치를 방지하여 변경된 태그만 업데이트됨
      if (callbacks?.onSuccess) callbacks.onSuccess();
    },
  });
};

// Tag Detail mutation
export const useTagDetail = () => {
  return useMutation({
    mutationFn: (code: TagKey) => tagDashboardApi.getTagDetail({ code }),
  });
};

// Tag Ban 삭제 mutation
export const useDeleteTagBan = (callbacks?: UseMutationCallback) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: TagBan) => tagDashboardApi.deleteTagBan(data),
    onMutate: async (data) => {
      // 진행 중인 쿼리 취소하여 낙관적 업데이트가 덮어써지지 않도록 함
      await queryClient.cancelQueries({ queryKey: tagDashboardKeys.dashboard() });

      // 이전 데이터 백업 (롤백용)
      const previousData = queryClient.getQueryData(tagDashboardKeys.dashboard());

      // 낙관적으로 캐시 업데이트 (해당 태그만)
      queryClient.setQueryData(tagDashboardKeys.dashboard(), (old: TagDashboard) => {
        if (!old) return old;

        return {
          ...old,
          tags: old.tags.map((tag: CategoryTags) =>
            tag.tagCode === data.tagCode
              ? { ...tag, excludedYn: false, recommendationYn: tag.lockedYn ? false : true } // 추천 포함
              : tag,
          ),
        };
      });

      // context로 이전 데이터 반환
      return { previousData };
    },
    onError: (error, data, context) => {
      // 에러 발생 시 이전 데이터로 롤백
      if (context?.previousData) {
        queryClient.setQueryData(tagDashboardKeys.dashboard(), context.previousData);
      }
      if (callbacks?.onError) callbacks.onError(error);
    },
    onSuccess: () => {
      // invalidateQueries 제거 (낙관적 업데이트로 이미 반영됨)
      // 전체 리페치를 방지하여 변경된 태그만 업데이트됨
      if (callbacks?.onSuccess) callbacks.onSuccess();
    },
  });
};
