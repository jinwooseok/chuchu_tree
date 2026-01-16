'use client';

import { useState } from 'react';
import { Search, ChevronDown, ChevronRight } from 'lucide-react';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible';
import { Input } from '@/components/ui/input';
import { useTagDashboardSidebarStore, SortBy, SortByName } from '@/lib/store/tagDashboard';
import { useTagDashboard } from '@/entities/tag-dashboard';
import { CategoryName } from '@/shared/constants/tagSystem';
import { getLevelColorClasses } from '@/features/tag-dashboard/lib/utils';
import { AppTooltip } from '@/components/custom/tooltip/AppTooltip';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { Button } from '@/components/ui/button';

export default function TagSidebar() {
  const { searchQuery, sortBy, selectedTagId, setSearchQuery, setSortBy, setSelectedTagId } = useTagDashboardSidebarStore();
  const { data: tagDashboard } = useTagDashboard();
  const [isSortingOpen, setIsSortingOpen] = useState(false);

  // 카테고리별 열림/닫힘 상태
  const [openCategories, setOpenCategories] = useState<Record<CategoryName, boolean>>({
    INTERMEDIATE: false,
    ADVANCED: false,
    MASTER: false,
    LOCKED: false,
    EXCLUDED: false,
  });

  const categoryTooltip = {
    INTERMEDIATE: '취약한 유형',
    ADVANCED: '익숙한 유형',
    MASTER: '충분히 숙련된 유형',
    EXCLUDED: '문제 추천 제외된 유형',
    LOCKED: '추천 조건 미달 유형',
  };

  // 카테고리 토글
  const toggleCategory = (categoryName: CategoryName) => {
    setOpenCategories((prev) => ({ ...prev, [categoryName]: !prev[categoryName] }));
  };

  // 태그 클릭 핸들러
  const handleTagClick = (tagId: number) => {
    if (selectedTagId === tagId) {
      setSelectedTagId(null); // 같은 태그 다시 클릭시 필터 해제
    } else {
      setSelectedTagId(tagId);
    }
  };

  // 로딩 상태
  if (!tagDashboard) {
    return (
      <div className="flex h-full items-center justify-center p-4">
        <p className="text-muted-foreground text-sm">로딩 중...</p>
      </div>
    );
  }

  return (
    <div className="hide-scrollbar flex h-full flex-col gap-4 overflow-y-auto p-4 text-sm">
      {/* 제목 */}
      <div className="cursor-default text-lg font-semibold">알고리즘 Dashboard</div>

      {/* 정렬 드롭다운 */}
      <div className="flex w-full flex-col gap-2">
        <label className="text-muted-foreground text-xs">정렬 기준</label>
        <Popover open={isSortingOpen} onOpenChange={setIsSortingOpen}>
          <PopoverTrigger asChild>
            <Button aria-label="정렬기준" variant="outline" className="w-full cursor-pointer justify-between text-xs">
              {SortByName[sortBy]}
              <ChevronDown className="ml-2 h-4 w-4" />
            </Button>
          </PopoverTrigger>
          <PopoverContent className="p-2" style={{ width: 'var(--radix-popover-trigger-width)' }}>
            {Object.entries(SortByName).map(([sortKey, sortKr]) => (
              <div
                aria-label={sortKr}
                key={sortKey}
                onClick={() => {
                  setSortBy(sortKey as SortBy);
                  setIsSortingOpen(false);
                }}
                className="hover:bg-innerground-hovergray flex cursor-pointer items-start rounded py-1 pl-2 text-xs"
              >
                {sortKr}
              </div>
            ))}
          </PopoverContent>
        </Popover>
      </div>

      {/* 검색 입력 */}
      <div className="relative">
        <Search className="text-muted-foreground absolute top-1/2 left-2 h-4 w-4 -translate-y-1/2" />
        <Input type="text" placeholder="태그 검색..." value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)} className="pl-8" />
      </div>

      {/* 카테고리별 태그 리스트 */}
      <div className="flex flex-col gap-2">
        {tagDashboard.categories.map((category) => {
          const levelColors = getLevelColorClasses(category.categoryName);
          const isOpen = openCategories[category.categoryName];

          return (
            <Collapsible key={category.categoryName} open={isOpen} onOpenChange={() => toggleCategory(category.categoryName)}>
              <AppTooltip content={categoryTooltip[category.categoryName]} side="right">
                <CollapsibleTrigger className="hover:bg-innerground-hovergray flex w-full items-center justify-between rounded-md p-2" aria-label={isOpen ? '섹션 접기' : '섹션 펼치기'}>
                  <div className="flex items-center gap-2">
                    {isOpen ? <ChevronDown className="h-4 w-4" aria-hidden="true" /> : <ChevronRight className="h-4 w-4" aria-hidden="true" />}
                    <span className={`${levelColors.bg} ${levelColors.text} rounded px-2 py-0.5 text-xs font-semibold`}>{category.categoryName}</span>
                    <span className="text-muted-foreground text-xs">({category.tags.length})</span>
                  </div>
                </CollapsibleTrigger>
              </AppTooltip>

              <CollapsibleContent className="mt-1 flex flex-col gap-1 pl-6">
                {category.tags.map((tag) => (
                  <button
                    key={tag.tagId}
                    onClick={() => handleTagClick(tag.tagId)}
                    className={`hover:text-primary text-left text-xs transition-colors ${selectedTagId === tag.tagId ? 'text-primary font-semibold' : 'text-muted-foreground'}`}
                  >
                    {tag.tagDisplayName}
                  </button>
                ))}
              </CollapsibleContent>
            </Collapsible>
          );
        })}
      </div>
    </div>
  );
}
