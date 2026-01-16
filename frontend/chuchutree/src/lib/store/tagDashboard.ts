import { create } from 'zustand';

export const SortByName = {
  default: '기본순',
  name: '이름순',
  lastSolved: '마지막 풀이순',
  level: '등급순',
};
export type SortBy = keyof typeof SortByName;

interface TagDashboardStore {
  // 상태
  searchQuery: string;
  sortBy: SortBy;
  selectedTagId: number | null;

  // 액션
  setSearchQuery: (query: string) => void;
  setSortBy: (sortBy: SortBy) => void;
  setSelectedTagId: (tagId: number | null) => void;
  clearFilters: () => void;
}

// 태그 사이드바 store 필터링 + 검색 + sorting
export const useTagDashboardSidebarStore = create<TagDashboardStore>((set) => ({
  // 초기 상태
  searchQuery: '',
  sortBy: 'default',
  selectedTagId: null,

  // 검색어 설정
  setSearchQuery: (query: string) => {
    set({ searchQuery: query });
  },

  // 정렬 기준 설정
  setSortBy: (sortBy: SortBy) => {
    set({ sortBy });
  },

  // 선택된 태그 ID 설정
  setSelectedTagId: (tagId: number | null) => {
    set({ selectedTagId: tagId });
  },

  // 필터 초기화
  clearFilters: () => {
    set({ searchQuery: '', sortBy: 'default', selectedTagId: null });
  },
}));
