'use client';

import { useMemo, useState, useCallback } from 'react';
import TagCard from '@/features/tag-dashboard/ui/TagCard';
import { TagDetailCard } from '@/features/tag-dashboard/ui/TagDetailCard';
import { useTagDashboardSidebarStore } from '@/lib/store/tagDashboard';
import { TagDashboard as TagDashboardType } from '@/entities/tag-dashboard';
import { calculateProgress } from '@/features/tag-dashboard/lib/utils';
import { useColumns } from '@/features/tag-dashboard/lib/useColumns';
import { TAG_INFO } from '@/shared/constants/tagSystem';

export function TagDashboard({ tagDashboard, isLanding = false }: { tagDashboard?: TagDashboardType; isLanding?: boolean }) {
  // store에서 필터/정렬 상태 가져오기
  const { searchQuery, sortBy, sortDirection, selectedTagId, categoryVisibility } = useTagDashboardSidebarStore();

  // 현재 뷰포트 컬럼 수 (1 / 2 / 3)
  const colCount = useColumns();

  // 확장된 태그 ID (detail 패널 표시)
  const [expandedTagId, setExpandedTagId] = useState<number | null>(null);

  const handleTagClick = useCallback((tagId: number) => {
    setExpandedTagId((prev) => (prev === tagId ? null : tagId));
  }, []);

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
      const query = searchQuery.toLowerCase();
      result = result.filter(
        (tag) =>
          tag.tagDisplayName.toLowerCase().includes(query) ||
          tag.tagCode.toLowerCase().includes(query) ||
          TAG_INFO[tag.tagCode].kr.toLowerCase().includes(query) ||
          tag.tagAliases.some((a) => a.alias.toLowerCase().includes(query)),
      );
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
          const comparison = TAG_INFO[a.tagCode].kr.localeCompare(TAG_INFO[b.tagCode].kr);
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

  // flat CSS Grid 배치를 위한 gridItems 계산
  // TagCard가 단일 grid 컨테이너 안에 유지되어 부모 이동(리마운트) 없이 style만 변경됨
  type TagWithProgress = (typeof filteredAndSortedTags)[0];
  type GridItem =
    | { type: 'card'; tag: TagWithProgress; row: number; col: number }
    | { type: 'detail'; tag: TagWithProgress; row: number; col: number; colSpan: number };

  const gridItems = useMemo((): GridItem[] => {
    const items: GridItem[] = [];
    const expandedIdx = expandedTagId !== null ? filteredAndSortedTags.findIndex((t) => t.tagId === expandedTagId) : -1;

    if (expandedIdx === -1) {
      filteredAndSortedTags.forEach((tag, i) => {
        items.push({ type: 'card', tag, row: Math.floor(i / colCount) + 1, col: (i % colCount) + 1 });
      });
      return items;
    }

    // expanded 이전 카드들
    for (let i = 0; i < expandedIdx; i++) {
      items.push({ type: 'card', tag: filteredAndSortedTags[i], row: Math.floor(i / colCount) + 1, col: (i % colCount) + 1 });
    }

    // expanded 카드는 항상 col 1 (행의 좌측)
    // expandedRow: 이전 카드들이 채운 행 수 + 1
    const expandedRow = Math.ceil(expandedIdx / colCount) + 1;
    items.push({ type: 'card', tag: filteredAndSortedTags[expandedIdx], row: expandedRow, col: 1 });

    // detail 카드: 1컬럼이면 다음 행, 2~3컬럼이면 같은 행의 나머지 열
    if (colCount === 1) {
      items.push({ type: 'detail', tag: filteredAndSortedTags[expandedIdx], row: expandedRow + 1, col: 1, colSpan: 1 });
    } else {
      items.push({ type: 'detail', tag: filteredAndSortedTags[expandedIdx], row: expandedRow, col: 2, colSpan: colCount - 1 });
    }

    // expanded 이후 카드들 (detail 행만큼 offset)
    const detailRowOffset = colCount === 1 ? 1 : 0;
    for (let i = expandedIdx + 1; i < filteredAndSortedTags.length; i++) {
      const afterIdx = i - expandedIdx - 1;
      items.push({
        type: 'card',
        tag: filteredAndSortedTags[i],
        row: expandedRow + 1 + detailRowOffset + Math.floor(afterIdx / colCount),
        col: (afterIdx % colCount) + 1,
      });
    }

    return items;
  }, [filteredAndSortedTags, expandedTagId, colCount]);

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
      {/* 단일 flat CSS Grid: TagCard가 부모 이동 없이 style만 변경되어 리마운트 방지 */}
      <div
        className="mx-auto py-1"
        style={{
          display: 'grid',
          gridTemplateColumns: `repeat(${colCount}, 320px)`,
          columnGap: '1rem',
          rowGap: '2rem',
          alignContent: 'start',
        }}
      >
        {gridItems.map((item) =>
          item.type === 'card' ? (
            <div key={item.tag.tagId} style={{ gridRow: item.row, gridColumn: item.col }}>
              <TagCard
                tag={item.tag}
                progress={item.tag.progress}
                isLanding={isLanding}
                onboardingId={item.tag.tagId === filteredAndSortedTags[0]?.tagId ? 'first-tag-card' : undefined}
                onTagClick={handleTagClick}
                isExpanded={item.tag.tagId === expandedTagId}
              />
            </div>
          ) : (
            <div
              key={`detail-${item.tag.tagId}`}
              style={{ gridRow: item.row, gridColumn: `${item.col} / span ${item.colSpan}` }}
              className="animate-in fade-in duration-200"
            >
              <TagDetailCard tag={item.tag} />
            </div>
          ),
        )}
      </div>
    </div>
  );
}
