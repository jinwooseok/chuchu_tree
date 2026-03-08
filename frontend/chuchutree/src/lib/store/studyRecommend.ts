import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';
import { StudyRecommendedProblem } from '@/entities/study';

interface StudyRecommendStore {
  // 스터디 전용 파라미터
  targetMemberId: number;
  recommendAllUnsolved: boolean;

  // 필터 상태 (useRecommendationStore와 동일 구조)
  selectedLevels: string[];
  selectedTagsList: string[];
  selectedExclusionMode: string;
  selectedCount: number;

  // 결과
  problems: StudyRecommendedProblem[];
  isLoading: boolean;

  // 표시 필터
  showFilters: {
    problemNumber: boolean;
    problemTier: boolean;
    recommendReason: boolean;
    algorithm: boolean;
  };

  // UI 섹션 토글
  showLevelSection: boolean;
  showTagSection: boolean;
  showFilterSection: boolean;
  showExcludedModeSection: boolean;

  // Actions
  setTargetMemberId: (id: number) => void;
  setRecommendAllUnsolved: (value: boolean) => void;
  setSelectedLevels: (levels: string[]) => void;
  setSelectedTagsList: (tags: string[]) => void;
  setSelectedExclusionMode: (mode: string) => void;
  setSelectedCount: (count: number) => void;
  setProblems: (problems: StudyRecommendedProblem[]) => void;
  setLoading: (isLoading: boolean) => void;
  toggleFilter: (filterName: keyof StudyRecommendStore['showFilters']) => void;
  resetFilters: () => void;
  toggleLevelSection: () => void;
  toggleTagSection: () => void;
  toggleFilterSection: () => void;
  toggleExcludedModeSection: () => void;
}

const initialFilters = {
  problemNumber: true,
  problemTier: true,
  recommendReason: true,
  algorithm: false,
};

const initialState = {
  targetMemberId: 0,
  recommendAllUnsolved: false,
  selectedLevels: [] as string[],
  selectedTagsList: [] as string[],
  selectedExclusionMode: 'LENIENT',
  selectedCount: 3,
  problems: [] as StudyRecommendedProblem[],
  isLoading: false,
  showFilters: { ...initialFilters },
  showLevelSection: false,
  showTagSection: false,
  showFilterSection: false,
  showExcludedModeSection: false,
};

export const useStudyRecommendStore = create<StudyRecommendStore>()(
  devtools(
    persist(
      immer((set) => ({
        ...initialState,

        setTargetMemberId: (id) =>
          set((state) => {
            state.targetMemberId = id;
          }),
        setRecommendAllUnsolved: (value) =>
          set((state) => {
            state.recommendAllUnsolved = value;
          }),
        setSelectedLevels: (levels) =>
          set((state) => {
            state.selectedLevels = levels;
          }),
        setSelectedTagsList: (tags) =>
          set((state) => {
            state.selectedTagsList = tags;
          }),
        setSelectedExclusionMode: (mode) =>
          set((state) => {
            state.selectedExclusionMode = mode;
          }),
        setSelectedCount: (count) =>
          set((state) => {
            state.selectedCount = count;
          }),
        setProblems: (problems) =>
          set((state) => {
            state.problems = problems;
          }),
        setLoading: (isLoading) =>
          set((state) => {
            state.isLoading = isLoading;
          }),
        toggleFilter: (filterName) =>
          set((state) => {
            state.showFilters[filterName] = !state.showFilters[filterName];
          }),
        resetFilters: () =>
          set((state) => {
            state.showFilters = { ...initialFilters };
          }),
        toggleLevelSection: () =>
          set((state) => {
            state.showLevelSection = !state.showLevelSection;
            state.showFilterSection = false;
            state.showExcludedModeSection = false;
          }),
        toggleTagSection: () =>
          set((state) => {
            state.showTagSection = !state.showTagSection;
          }),
        toggleFilterSection: () =>
          set((state) => {
            state.showFilterSection = !state.showFilterSection;
            state.showLevelSection = false;
            state.showExcludedModeSection = false;
          }),
        toggleExcludedModeSection: () =>
          set((state) => {
            state.showExcludedModeSection = !state.showExcludedModeSection;
            state.showLevelSection = false;
            state.showFilterSection = false;
          }),
      })),
      {
        name: 'study-recommend-storage',
        partialize: (state) => ({
          selectedLevels: state.selectedLevels,
          selectedTagsList: state.selectedTagsList,
          selectedExclusionMode: state.selectedExclusionMode,
          selectedCount: state.selectedCount,
          showFilters: state.showFilters,
          showLevelSection: state.showLevelSection,
          showTagSection: state.showTagSection,
          showFilterSection: state.showFilterSection,
          showExcludedModeSection: state.showExcludedModeSection,
          recommendAllUnsolved: state.recommendAllUnsolved,
        }),
      },
    ),
    { name: 'StudyRecommendStore' },
  ),
);
