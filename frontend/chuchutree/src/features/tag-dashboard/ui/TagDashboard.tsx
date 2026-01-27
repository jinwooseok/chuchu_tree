'use client';

import { useMemo } from 'react';
import TagCard from '@/features/tag-dashboard/ui/TagCard';
import { useTagDashboardSidebarStore } from '@/lib/store/tagDashboard';
import { TagDashboard as TagDashboardType } from '@/entities/tag-dashboard';
import { calculateProgress } from '@/features/tag-dashboard/lib/utils';

export function TagDashboard({ tagDashboard, isLanding = false }: { tagDashboard?: TagDashboardType; isLanding?: boolean }) {
  // store에서 필터/정렬 상태 가져오기
  const { searchQuery, sortBy, sortDirection, selectedTagId, categoryVisibility } = useTagDashboardSidebarStore();

  // 필터링 및 정렬된 태그 목록 (progress 포함)
  const filteredAndSortedTags = useMemo(() => {
    if (!tagDashboard) return [];

    // 각 태그에 progress 계산하여 추가
    let result = tagDashboard.tags.map((tag) => {
      const progress = calculateProgress({
        solvedCnt: tag.accountStat.solvedProblemCount,
        requireSolveCnt: tag.nextLevelStat.solvedProblemCount,
        userTier: tag.accountStat.requiredMinTier,
        requireTier: tag.nextLevelStat.requiredMinTier,
        highest: tag.accountStat.higherProblemTier,
        requireHighest: tag.nextLevelStat.higherProblemTier,
      });
      return { ...tag, progress };
    });

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
      case 'progress':
        result.sort((a, b) => {
          const comparison = b.progress - a.progress; // 높은 progress가 먼저 오도록
          return sortDirection === 'asc' ? comparison : -comparison; // asc가 기본(높은 순)
        });
        break;
      case 'default':
        result.sort((a, b) => {
          const comparison = b.accountStat.solvedProblemCount - a.accountStat.solvedProblemCount;
          return sortDirection === 'asc' ? comparison : -comparison;
        });
        break;
      default:
        // 알 수 없는 정렬 기준은 그대로 유지
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
          <TagCard key={tag.tagId} tag={tag} progress={tag.progress} isLanding={isLanding} />
        ))}
      </div>
    </div>
  );
}
