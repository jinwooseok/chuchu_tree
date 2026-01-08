import { TagDashboard } from '@/entities/tag-dashboard';
import { create } from 'zustand';
import { combine, devtools } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';

export type SortBy = 'default' | 'name' | 'lastSolved' | 'level';

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


type State = {
  categories: TagDashboard['categories'];
  tags: TagDashboard['tags'];
  isInitialized: boolean;
};

const initialState: State = {
  categories: [],
  tags: [],
  isInitialized: false,
};

// TagDashboard Data Store
const TagDashboardStoreInternal = create(
  devtools(
    immer(
      combine(initialState, (set, get) => ({
        actions: {
          setTagDashboardData: (tagDashboard: TagDashboard) => {
            set((state) => {
              state.categories = tagDashboard.categories;
              state.tags = tagDashboard.tags;
              state.isInitialized = true;
            });
          },
          clearTagDashboardData: () => {
            set((state) => {
              state.categories = [];
              state.tags = [];
              state.isInitialized = false;
            });
          },
        },
        // Selectors
        getTagById: (tagId: number) => {
          return get().tags.find((tag) => tag.tagId === tagId);
        },
        getTagsByCategory: (categoryName: string) => {
          const category = get().categories.find((cat) => cat.categoryName === categoryName);
          return category?.tags || [];
        },
      })),
    ),
    { name: 'TagDashboardStore' },
  ),
);

// Selectors
export const useTagDashboardStore = () => {
  const store = TagDashboardStoreInternal();
  return store as typeof store & State;
};

export const useSetTagDashboardData = () => {
  const setTagDashboard = TagDashboardStoreInternal((s) => s.actions.setTagDashboardData);
  return setTagDashboard;
};

export const useClearTagDashboardData = () => {
  const clearTagDashboard = TagDashboardStoreInternal((s) => s.actions.clearTagDashboardData);
  return clearTagDashboard;
};
