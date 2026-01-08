'use client';

import { useMemo } from 'react';
import TagCard from '@/features/tag-dashboard/ui/TagCard';
import { useTagDashboardSidebarStore, useTagDashboardStore } from '@/lib/store/tagDashboard';

export default function TagDashboard() {
  // store에서 태그 목록 가져오기
  const { tags, isInitialized } = useTagDashboardStore();

  // store에서 필터/정렬 상태 가져오기
  const { searchQuery, sortBy, selectedTagId } = useTagDashboardSidebarStore();

  // 필터링 및 정렬된 태그 목록
  const filteredAndSortedTags = useMemo(() => {
    let result = [...tags];

    // 검색어 필터링
    if (searchQuery) {
      result = result.filter((tag) => tag.tagDisplayName.toLowerCase().includes(searchQuery.toLowerCase()));
    }

    // 선택된 태그 필터링 (sidebar에서 클릭한 경우)
    if (selectedTagId !== null) {
      result = result.filter((tag) => tag.tagId === selectedTagId);
    }

    // 정렬
    switch (sortBy) {
      case 'name':
        result.sort((a, b) => a.tagDisplayName.localeCompare(b.tagDisplayName));
        break;
      case 'lastSolved':
        result.sort((a, b) => new Date(b.accountStat.lastSolvedDate).getTime() - new Date(a.accountStat.lastSolvedDate).getTime());
        break;
      case 'level':
        const levelOrder = { MASTER: 0, ADVANCED: 1, IMEDIATED: 2, EXCLUDED: 3, LOCKED: 4 };
        result.sort((a, b) => levelOrder[a.accountStat.currentLevel as keyof typeof levelOrder] - levelOrder[b.accountStat.currentLevel as keyof typeof levelOrder]);
        break;
      case 'default':
      default:
        // 기본순은 API 응답 순서 유지
        break;
    }

    return result;
  }, [tags, searchQuery, sortBy, selectedTagId]);

  // 데이터 로딩 중
  if (!isInitialized) {
    return (
      <div className="flex h-full w-full items-center justify-center">
        <p className="text-muted-foreground">로딩 중...</p>
      </div>
    );
  }

  return (
    <div className="hide-scrollbar grid h-full w-full grid-cols-2 content-start gap-4 overflow-y-auto lg:grid-cols-3">
      {filteredAndSortedTags.length > 0 ? (
        filteredAndSortedTags.map((tag) => <TagCard key={tag.tagId} tag={tag} />)
      ) : (
        <div className="col-span-full flex h-full items-center justify-center">
          <p className="text-muted-foreground">검색 결과가 없습니다.</p>
        </div>
      )}
    </div>
  );
}
