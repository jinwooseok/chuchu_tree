'use client';

import { useMemo } from 'react';
import TagCard from '@/features/tag-dashboard/ui/TagCard';
import { useTagDashboardSidebarStore } from '@/lib/store/tagDashboard';
import { useTagDashboard } from '@/entities/tag-dashboard';

export default function TagDashboard() {
  // TanStack Query에서 태그 데이터 가져오기
  const { data: tagDashboard } = useTagDashboard();

  // store에서 필터/정렬 상태 가져오기
  const { searchQuery, sortBy, sortDirection, selectedTagId, categoryVisibility } = useTagDashboardSidebarStore();

  // 필터링 및 정렬된 태그 목록
  const filteredAndSortedTags = useMemo(() => {
    if (!tagDashboard) return [];

    let result = [...tagDashboard.tags];

    // 검색어 필터링
    if (searchQuery) {
      result = result.filter((tag) => tag.tagDisplayName.toLowerCase().includes(searchQuery.toLowerCase()));
    }

    // 선택된 태그 필터링 (sidebar에서 클릭한 경우)
    if (selectedTagId !== null) {
      result = result.filter((tag) => tag.tagId === selectedTagId);
    }

    // 카테고리 visibility 필터링
    result = result.filter((tag) => {
      // EXCLUDED는 excludedYn으로 판단
      if (tag.excludedYn) {
        return categoryVisibility.EXCLUDED;
      }
      // 나머지는 currentLevel로 판단
      return categoryVisibility[tag.accountStat.currentLevel];
    });

    // 정렬
    switch (sortBy) {
      case 'name':
        result.sort((a, b) => {
          const comparison = a.tagDisplayName.localeCompare(b.tagDisplayName);
          return sortDirection === 'asc' ? comparison : -comparison;
        });
        break;
      case 'lastSolved':
        result.sort((a, b) => {
          const comparison = new Date(b.accountStat.lastSolvedDate).getTime() - new Date(a.accountStat.lastSolvedDate).getTime();
          return sortDirection === 'asc' ? -comparison : comparison;
        });
        break;
      case 'level':
        const levelOrder = { MASTER: 3, ADVANCED: 2, INTERMEDIATE: 1, EXCLUDED: 0, LOCKED: 4 };
        result.sort((a, b) => {
          const comparison = levelOrder[a.accountStat.currentLevel as keyof typeof levelOrder] - levelOrder[b.accountStat.currentLevel as keyof typeof levelOrder];
          return sortDirection === 'asc' ? comparison : -comparison;
        });
        break;
      case 'default':
      default:
        // 기본순은 API 응답 순서 유지 (방향 무시)
        break;
    }

    return result;
  }, [tagDashboard, searchQuery, sortBy, sortDirection, selectedTagId, categoryVisibility]);

  // 데이터 로딩 중
  if (!tagDashboard) {
    return (
      <div className="flex h-full w-full items-center justify-center">
        <p className="text-muted-foreground">로딩 중...</p>
      </div>
    );
  }
  if (filteredAndSortedTags.length === 0) {
    return (
      <div className="flex h-full w-full items-center justify-center">
        <p className="text-muted-foreground">검색 결과가 없습니다.</p>
      </div>
    );
  }

  return (
    <div className="hide-scrollbar flex h-full w-full overflow-y-auto">
      <div className="mx-auto grid w-fit grid-cols-1 content-start gap-x-4 gap-y-8 lg:grid-cols-2 xl:grid-cols-3">
        {filteredAndSortedTags.map((tag) => (
          <TagCard key={tag.tagId} tag={tag} />
        ))}
      </div>
    </div>
  );
}
