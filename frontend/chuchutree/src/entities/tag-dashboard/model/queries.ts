'use client';

import { tagDashboardApi } from '../api/tagDashboard.api';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Categories, CategoryTags, TagBan, TagDashboard } from './tagDashboard.types';
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
      await queryClient.cancelQueries({ queryKey: tagDashboardKeys.dashboard() });

      const previousData = queryClient.getQueryData(tagDashboardKeys.dashboard());

      queryClient.setQueryData(tagDashboardKeys.dashboard(), (old: TagDashboard) => {
        if (!old) return old;

        const targetTag = old.tags.find((tag: CategoryTags) => tag.tagCode === data.tagCode);

        const updatedTags = old.tags.map((tag: CategoryTags) =>
          tag.tagCode === data.tagCode
            ? { ...tag, excludedYn: true, recommendationYn: false }
            : tag,
        );

        let updatedCategories = old.categories;
        if (targetTag) {
          const tagInfo = { tagId: targetTag.tagId, tagCode: targetTag.tagCode, tagDisplayName: targetTag.tagDisplayName };
          updatedCategories = old.categories.map((category: Categories) => {
            if (category.categoryName === 'EXCLUDED') {
              const alreadyThere = category.tags.some((t) => t.tagId === targetTag.tagId);
              return alreadyThere ? category : { ...category, tags: [...category.tags, tagInfo] };
            }
            return { ...category, tags: category.tags.filter((t) => t.tagId !== targetTag.tagId) };
          });
        }

        return { ...old, tags: updatedTags, categories: updatedCategories };
      });

      return { previousData };
    },
    onError: (error, _data, context) => {
      if (context?.previousData) {
        queryClient.setQueryData(tagDashboardKeys.dashboard(), context.previousData);
      }
      if (callbacks?.onError) callbacks.onError(error);
    },
    onSuccess: () => {
      if (callbacks?.onSuccess) callbacks.onSuccess();
    },
  });
};

// Tag Detail query (useQuery로 캐싱 활성화 - 한번 본 태그는 재요청 없이 즉시 표시)
export const useTagDetail = (code: TagKey) => {
  return useQuery({
    queryKey: tagDashboardKeys.detail(code),
    queryFn: () => tagDashboardApi.getTagDetail({ code }),
  });
};

// Tag Ban 삭제 mutation
export const useDeleteTagBan = (callbacks?: UseMutationCallback) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: TagBan) => tagDashboardApi.deleteTagBan(data),
    onMutate: async (data) => {
      await queryClient.cancelQueries({ queryKey: tagDashboardKeys.dashboard() });

      const previousData = queryClient.getQueryData(tagDashboardKeys.dashboard());

      queryClient.setQueryData(tagDashboardKeys.dashboard(), (old: TagDashboard) => {
        if (!old) return old;

        const targetTag = old.tags.find((tag: CategoryTags) => tag.tagCode === data.tagCode);

        const updatedTags = old.tags.map((tag: CategoryTags) =>
          tag.tagCode === data.tagCode
            ? { ...tag, excludedYn: false, recommendationYn: tag.lockedYn ? false : true }
            : tag,
        );

        let updatedCategories = old.categories;
        if (targetTag) {
          const tagInfo = { tagId: targetTag.tagId, tagCode: targetTag.tagCode, tagDisplayName: targetTag.tagDisplayName };
          const targetCategoryName = targetTag.lockedYn ? 'LOCKED' : targetTag.accountStat.currentLevel;
          updatedCategories = old.categories.map((category: Categories) => {
            if (category.categoryName === targetCategoryName) {
              const alreadyThere = category.tags.some((t) => t.tagId === targetTag.tagId);
              return alreadyThere ? category : { ...category, tags: [...category.tags, tagInfo] };
            }
            if (category.categoryName === 'EXCLUDED') {
              return { ...category, tags: category.tags.filter((t) => t.tagId !== targetTag.tagId) };
            }
            return category;
          });
        }

        return { ...old, tags: updatedTags, categories: updatedCategories };
      });

      return { previousData };
    },
    onError: (error, _data, context) => {
      if (context?.previousData) {
        queryClient.setQueryData(tagDashboardKeys.dashboard(), context.previousData);
      }
      if (callbacks?.onError) callbacks.onError(error);
    },
    onSuccess: () => {
      if (callbacks?.onSuccess) callbacks.onSuccess();
    },
  });
};
