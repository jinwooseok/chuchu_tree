'use client';

import { useState } from 'react';
import { Search, ChevronDown, ChevronRight } from 'lucide-react';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible';
import { Input } from '@/components/ui/input';
import { useTagDashboardSidebarStore, useTagDashboardStore, SortBy } from '@/lib/store/tagDashboard';
import { CategoryName } from '@/shared/constants/tagSystem';
import { getLevelColorClasses } from '@/features/tag-dashboard/lib/utils';

export default function TagSidebar() {
  const { searchQuery, sortBy, selectedTagId, setSearchQuery, setSortBy, setSelectedTagId } = useTagDashboardSidebarStore();
  const { categories, isInitialized } = useTagDashboardStore();

  // 카테고리별 열림/닫힘 상태
  const [openCategories, setOpenCategories] = useState<Record<CategoryName, boolean>>({
    INTERMEDIATE: false,
    ADVANCED: false,
    MASTER: false,
    LOCKED: false,
    EXCLUDED: false,
  });

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
  if (!isInitialized) {
    return (
      <div className="flex h-full items-center justify-center p-4">
        <p className="text-muted-foreground text-sm">로딩 중...</p>
      </div>
    );
  }

  return (
    <div className="hide-scrollbar flex h-full flex-col gap-4 overflow-y-auto p-4 text-sm">
      {/* 제목 */}
      <div className="text-lg font-semibold">알고리즘 Dashboard</div>

      {/* 정렬 드롭다운 */}
      <div className="flex flex-col gap-2">
        <label className="text-muted-foreground text-xs">정렬 기준</label>
        <select
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value as SortBy)}
          className="border-input bg-background ring-offset-background focus-visible:ring-ring flex h-9 w-full rounded-md border px-3 py-1 text-sm shadow-sm transition-colors focus-visible:ring-1 focus-visible:outline-none"
        >
          <option value="default">기본순</option>
          <option value="name">이름순</option>
          <option value="lastSolved">마지막 풀이날짜순</option>
          <option value="level">태그 등급순</option>
        </select>
      </div>

      {/* 검색 입력 */}
      <div className="relative">
        <Search className="text-muted-foreground absolute top-1/2 left-2 h-4 w-4 -translate-y-1/2" />
        <Input type="text" placeholder="태그 검색..." value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)} className="pl-8" />
      </div>

      {/* 카테고리별 태그 리스트 */}
      <div className="flex flex-col gap-2">
        {categories.map((category) => {
          const levelColors = getLevelColorClasses(category.categoryName);
          const isOpen = openCategories[category.categoryName];

          return (
            <Collapsible key={category.categoryName} open={isOpen} onOpenChange={() => toggleCategory(category.categoryName)}>
              <CollapsibleTrigger className="flex w-full items-center justify-between rounded-md p-2 hover:bg-gray-100">
                <div className="flex items-center gap-2">
                  {isOpen ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
                  <span className={`${levelColors.bg} ${levelColors.text} rounded px-2 py-0.5 text-xs font-semibold`}>{category.categoryName}</span>
                  <span className="text-muted-foreground text-xs">({category.tags.length})</span>
                </div>
              </CollapsibleTrigger>

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
