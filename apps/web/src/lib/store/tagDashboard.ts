import { create } from 'zustand';
import { CategoryName } from '@/shared/constants/tagSystem';

export const SortByName = {
  progress: '승급임박순',
  name: '이름순',
  lastSolved: '마지막 풀이순',
  level: '등급순',
  default: '풀이수 순',
};
export type SortBy = keyof typeof SortByName;

export type SortDirection = 'asc' | 'desc';

export const SortDirectionName = {
  asc: '오름차순',
  desc: '내림차순',
};

const DEFAULT_CATEGORY_ORDER: CategoryName[] = ['INTERMEDIATE', 'ADVANCED', 'MASTER', 'LOCKED', 'EXCLUDED'];

interface TagDashboardStore {
  // 상태
  searchQuery: string;
  sortBy: SortBy;
  sortDirection: SortDirection;
  selectedTagId: number | null;
  categoryVisibility: Record<CategoryName, boolean>;
  categoryOrder: CategoryName[];

  // 액션
  setSearchQuery: (query: string) => void;
  setSortBy: (sortBy: SortBy) => void;
  setSortDirection: (direction: SortDirection) => void;
  setSelectedTagId: (tagId: number | null) => void;
  toggleCategoryVisibility: (category: CategoryName) => void;
  setCategoryOrder: (order: CategoryName[]) => void;
  clearFilters: () => void;
}

// 태그 사이드바 store 필터링 + 검색 + sorting
export const useTagDashboardSidebarStore = create<TagDashboardStore>((set) => ({
  // 초기 상태
  searchQuery: '',
  sortBy: 'progress',
  sortDirection: 'asc',
  selectedTagId: null,
  categoryVisibility: {
    INTERMEDIATE: true,
    ADVANCED: true,
    MASTER: false,
    LOCKED: true,
    EXCLUDED: false,
  },
  categoryOrder: DEFAULT_CATEGORY_ORDER,

  // 검색어 설정
  setSearchQuery: (query: string) => {
    set({ searchQuery: query });
  },

  // 정렬 기준 설정
  setSortBy: (sortBy: SortBy) => {
    set({ sortBy });
    // 승급임박순 선택 시 MASTER와 EXCLUDED 카테고리 자동 off
    if (sortBy === 'progress') {
      set((state) => ({
        categoryVisibility: {
          ...state.categoryVisibility,
          MASTER: false,
          EXCLUDED: false,
        },
      }));
    }
  },

  // 정렬 방향 설정
  setSortDirection: (direction: SortDirection) => {
    set({ sortDirection: direction });
  },

  // 선택된 태그 ID 설정
  setSelectedTagId: (tagId: number | null) => {
    set({ selectedTagId: tagId });
  },

  // 카테고리 표시/숨김 토글
  toggleCategoryVisibility: (category: CategoryName) => {
    set((state) => ({
      categoryVisibility: {
        ...state.categoryVisibility,
        [category]: !state.categoryVisibility[category],
      },
    }));
  },

  // 카테고리 순서 설정
  setCategoryOrder: (order: CategoryName[]) => {
    set({ categoryOrder: order });
  },

  // 필터 초기화
  clearFilters: () => {
    set({
      searchQuery: '',
      sortBy: 'progress',
      sortDirection: 'asc',
      selectedTagId: null,
      categoryVisibility: {
        INTERMEDIATE: true,
        ADVANCED: true,
        MASTER: false,
        LOCKED: true,
        EXCLUDED: false,
      },
      categoryOrder: DEFAULT_CATEGORY_ORDER,
    });
  },
}));
