'use client';

import { useState, useId } from 'react';
import { Search, ChevronDown, ChevronRight, GripVertical, RotateCcw, ArrowUpDown } from 'lucide-react';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible';
import { Input } from '@/components/ui/input';
import { useTagDashboardSidebarStore, SortBy, SortByName } from '@/lib/store/tagDashboard';
import type { Categories, TagDashboard as TagDashboardType } from '@/entities/tag-dashboard';
import { CategoryName } from '@/shared/constants/tagSystem';
import { getLevelColorClasses } from '@/features/tag-dashboard/lib/utils';
import { AppTooltip } from '@/components/custom/tooltip/AppTooltip';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { Button } from '@/components/ui/button';
import { DndContext, closestCenter, KeyboardSensor, PointerSensor, useSensor, useSensors, DragEndEvent } from '@dnd-kit/core';
import { arrayMove, SortableContext, sortableKeyboardCoordinates, useSortable, verticalListSortingStrategy } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import { Switch } from '@/components/ui/switch';
import HelpPopover from '@/shared/ui/help-popover';

// 드래그 가능한 카테고리 컴포넌트
interface DraggableCategoryProps {
  categoryName: CategoryName;
  category: Categories;
  isOpen: boolean;
  isVisible: boolean;
  onToggleOpen: () => void;
  onToggleVisibility: () => void;
  onTagClick: (tagId: number) => void;
  selectedTagId: number | null;
  categoryTooltip: Record<CategoryName, string>;
}

function DraggableCategory({ categoryName, category, isOpen, isVisible, onToggleOpen, onToggleVisibility, onTagClick, selectedTagId, categoryTooltip }: DraggableCategoryProps) {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({ id: categoryName });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
  };

  const levelColors = getLevelColorClasses(categoryName);

  return (
    <div ref={setNodeRef} style={style}>
      <Collapsible open={isOpen} onOpenChange={onToggleOpen}>
        <div className="flex items-center gap-2">
          {/* 드래그 핸들 */}
          <button {...attributes} {...listeners} className="text-muted-foreground hover:text-foreground cursor-grab active:cursor-grabbing" aria-label="카테고리 순서 변경">
            <GripVertical className="h-4 w-4" />
          </button>

          {/* 카테고리 토글 트리거 */}
          <AppTooltip content={categoryTooltip[categoryName]} side="right">
            <CollapsibleTrigger className="hover:bg-innerground-hovergray flex flex-1 items-center justify-between rounded-md p-2" aria-label={isOpen ? '섹션 접기' : '섹션 펼치기'}>
              <div className="flex items-center gap-2">
                {isOpen ? <ChevronDown className="h-4 w-4" aria-hidden="true" /> : <ChevronRight className="h-4 w-4" aria-hidden="true" />}
                <span className={`${levelColors.bg} ${levelColors.text} rounded px-2 py-0.5 text-xs font-semibold`}>{categoryName}</span>
                <span className="text-muted-foreground text-xs">({category.tags.length})</span>
              </div>
            </CollapsibleTrigger>
          </AppTooltip>

          {/* 표시/숨김 토글 */}
          <AppTooltip content={isVisible ? '숨기기' : '보이기'} side="right">
            <Switch checked={isVisible} onCheckedChange={onToggleVisibility} aria-label="카테고리 표시/숨김" />
          </AppTooltip>
        </div>

        <CollapsibleContent className="mt-1 flex flex-col gap-1 pl-6">
          {category.tags.map((tag) => (
            <button
              key={tag.tagId}
              onClick={() => onTagClick(tag.tagId)}
              className={`hover:text-primary text-left text-xs transition-colors ${selectedTagId === tag.tagId ? 'text-primary font-semibold' : 'text-muted-foreground'}`}
            >
              {tag.tagDisplayName}
            </button>
          ))}
        </CollapsibleContent>
      </Collapsible>
    </div>
  );
}

export function TagSidebarInset({ tagDashboard, isLanding = false }: { tagDashboard?: TagDashboardType; isLanding?: boolean }) {
  const {
    searchQuery,
    sortBy,
    sortDirection,
    selectedTagId,
    categoryVisibility,
    categoryOrder,
    setSearchQuery,
    setSortBy,
    setSortDirection,
    setSelectedTagId,
    toggleCategoryVisibility,
    setCategoryOrder,
    clearFilters,
  } = useTagDashboardSidebarStore();
  const [isSortingOpen, setIsSortingOpen] = useState(false);
  const categoryContextId = useId();

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

  // 드래그 센서 설정
  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 8,
      },
    }),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    }),
  );

  // 카테고리 토글
  const toggleCategory = (categoryName: CategoryName) => {
    setOpenCategories((prev) => ({ ...prev, [categoryName]: !prev[categoryName] }));
  };

  // 카테고리 순서 변경
  const handleCategoryDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;

    if (!over || active.id === over.id) return;

    const oldIndex = categoryOrder.findIndex((c) => c === active.id);
    const newIndex = categoryOrder.findIndex((c) => c === over.id);

    const reorderedCategories = arrayMove(categoryOrder, oldIndex, newIndex);
    setCategoryOrder(reorderedCategories);
  };

  // 태그 클릭 핸들러
  const handleTagClick = (tagId: number) => {
    if (selectedTagId === tagId) {
      setSelectedTagId(null);
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

  // 카테고리를 categoryOrder에 따라 정렬
  const orderedCategories = categoryOrder.map((categoryName) => tagDashboard.categories.find((c) => c.categoryName === categoryName)).filter((c) => c !== undefined);

  return (
    <div className="hide-scrollbar flex h-full flex-col gap-4 overflow-y-auto p-4 text-sm">
      {/* 제목과 초기화 버튼 */}
      {isLanding && <div className="bg-primary w-full cursor-default rounded-sm px-2 py-2 text-sm font-medium text-white select-none">ChuchuTree 튜토리얼</div>}
      <div className="flex items-center justify-between">
        <div className="cursor-default text-lg font-semibold">알고리즘 Dashboard</div>
        <HelpPopover width="w-85">
          <div className="space-y-2">
            <h4 className="text-sm font-semibold">알고리즘 유형별 나의 실력을 확인하세요.</h4>
            <div className="border px-2 py-2">
              <p className="text-sm">유형별 등급은 문제 추천 빈도에 반영됩니다.</p>
            </div>
            <p className="text-foreground text-xs">
              <span className="text-locked-text bg-locked-bg px-1">LOCKED</span> : 시작 전 유형
            </p>
            <p className="text-muted-foreground ml-2 text-xs">└ 추천에 포함되지 않습니다. 시작 조건을 달성하세요</p>
            <p className="text-foreground text-xs">
              <span className="text-intermediate-text bg-intermediate-bg px-1">INTERMEDIATE</span> : 아직 취약한 유형
            </p>
            <p className="text-muted-foreground ml-2 text-xs">└ 가장 먼저 추천됩니다.</p>
            <p className="text-foreground text-xs">
              <span className="text-advanced-text bg-advanced-bg px-1">ADVANCED</span> : 익숙해진 유형
            </p>
            <p className="text-muted-foreground ml-2 text-xs">└ 빈번하게 추천됩니다.</p>
            <p className="text-foreground text-xs">
              <span className="text-master-text bg-master-bg px-1">MASTER</span> : 마스터한 유형
            </p>
            <p className="text-muted-foreground ml-2 text-xs">└ 가끔 추천됩니다.</p>
            <p className="text-foreground text-xs">
              <span className="text-excluded-text bg-excluded-bg px-1">EXCLUDED</span> : 추천 제외된 유형
            </p>
            <p className="text-muted-foreground ml-2 text-xs">└ 추천에 포함되지 않습니다.</p>
            <div className="border px-2 py-2">
              <p className="text-sm">3가지 기준에 의해 등급이 결정됩니다.</p>
            </div>
            <p className="text-foreground text-xs">
              <span className="text-locked-text bg-locked-bg px-1">풀이 수</span> : 푼 문제수 / 다음 등급을 위한 최소 문제 수
            </p>
            <p className="text-foreground text-xs">
              <span className="text-locked-text bg-locked-bg px-1">최소 달성 티어</span> : 다음 등급을 위한 사용자 티어
            </p>
            <p className="text-foreground text-xs">
              <span className="text-locked-text bg-locked-bg px-1">최고 난이도</span> : 푼 문제 중 최고 티어 / 풀어야 할 문제의 티어
            </p>
            <p className="text-muted-foreground ml-2 text-xs">└ 해당 유형을 포함 하는 문제의 티어가 이 기준 보다 높아야 합니다.</p>
          </div>
        </HelpPopover>
      </div>

      {/* 정렬 기준 드롭다운 */}
      <div className="flex w-full flex-col gap-2">
        <label className="text-muted-foreground text-xs">정렬 기준</label>
        <div className="flex items-center gap-2">
          <Popover open={isSortingOpen} onOpenChange={setIsSortingOpen}>
            <PopoverTrigger asChild>
              <Button aria-label="정렬기준" variant="outline" className="flex-1 cursor-pointer justify-between text-xs">
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

          {/* 정렬 방향 토글 버튼 */}
          <AppTooltip content={sortDirection === 'asc' ? '오름차순' : '내림차순'} side="right">
            <Button
              onClick={() => setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc')}
              variant="outline"
              size="icon"
              aria-label="정렬방향 변경"
              className="text-muted-foreground hover:text-foreground relative shrink-0 cursor-pointer"
            >
              <ArrowUpDown className="h-4 w-4" />
              {sortDirection === 'desc' && <div className="bg-primary/80 absolute top-2 right-1.5 h-2 w-2 rounded-full" />}
            </Button>
          </AppTooltip>
        </div>
      </div>

      {/* 검색 입력 */}
      <div className="flex items-center justify-between gap-2">
        <div className="relative w-full">
          <Search className="text-muted-foreground absolute top-1/2 left-2 h-4 w-4 -translate-y-1/2" />
          <Input type="text" placeholder="태그 검색..." value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)} className="pl-8" />
        </div>
        <AppTooltip content="필터 초기화" side="right">
          <Button onClick={clearFilters} variant="outline" size="icon" aria-label="필터 초기화" className="text-muted-foreground hover:text-foreground shrink-0 cursor-pointer">
            <RotateCcw className="h-4 w-4" />
          </Button>
        </AppTooltip>
      </div>

      {/* 카테고리별 태그 리스트 (드래그 가능) */}
      <div className="flex flex-col gap-2">
        <DndContext id={categoryContextId} sensors={sensors} collisionDetection={closestCenter} onDragEnd={handleCategoryDragEnd}>
          <SortableContext items={categoryOrder} strategy={verticalListSortingStrategy}>
            {orderedCategories.map((category) => (
              <DraggableCategory
                key={category.categoryName}
                categoryName={category.categoryName}
                category={category}
                isOpen={openCategories[category.categoryName]}
                isVisible={categoryVisibility[category.categoryName]}
                onToggleOpen={() => toggleCategory(category.categoryName)}
                onToggleVisibility={() => toggleCategoryVisibility(category.categoryName)}
                onTagClick={handleTagClick}
                selectedTagId={selectedTagId}
                categoryTooltip={categoryTooltip}
              />
            ))}
          </SortableContext>
        </DndContext>
      </div>
    </div>
  );
}
