import { create } from 'zustand';
import { combine, devtools, persist } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';

type LevelType = 'easy' | 'normal' | 'hard' | 'extreme';

export interface RecommendedProblems {
  problemId: number;
  problemTitle: string;
  problemTierLevel: number;
  problemTierName: string;
  problemClassLevel: number;
  recommandReasons: {
    reason: string;
    additionalData: string;
  }[];
  tags: {
    tagId: number;
    tagCode: string;
    tagDisplayName: string;
    tagTargets: {
      targetId: number;
      targetCode: string;
      targetDisplayName: string;
    }[];
    tagAliases: {
      alias: string;
    }[];
  }[];
}

interface RecommendationHistoryItem {
  timestamp: number;
  problems: RecommendedProblems[];
}

type State = {
  // Filter state
  selectedLevels: string[]; // 복수 선택 지원 (기존 selectedLevel 대체)
  selectedTagsList: string[]; // 복수 선택 지원 (기존 selectedTags 대체)
  selectedExclusionMode: string; // 기존 selectedExcludedMode → selectedExclusionMode
  selectedCount: number; // 추천 문제 개수

  // Recommendation result
  problems: RecommendedProblems[];
  isLoading: boolean;
  error: Error | null;

  // Recommendation history
  recommendationHistory: RecommendationHistoryItem[];

  // Display options
  showFilters: {
    problemNumber: boolean;
    problemTier: boolean;
    recommendReason: boolean;
    algorithm: boolean;
  };

  // UI section visibility
  showLevelSection: boolean;
  showTagSection: boolean;
  showFilterSection: boolean;
  showExcludedModeSection: boolean;
};

const initialState: State = {
  selectedLevels: [],
  selectedTagsList: [],
  selectedExclusionMode: 'LENIENT',
  selectedCount: 3,
  problems: [],
  isLoading: false,
  error: null,
  recommendationHistory: [],
  showFilters: {
    problemNumber: true,
    problemTier: true,
    recommendReason: true,
    algorithm: false,
  },
  showLevelSection: false,
  showTagSection: false,
  showFilterSection: false,
  showExcludedModeSection: false,
};

const recommendationStoreInternal = create(
  devtools(
    persist(
      immer(
        combine(initialState, (set, get) => ({
          actions: {
            // Set selected levels (복수 선택)
            setSelectedLevels: (levels: string[]) => {
              set((state) => {
                state.selectedLevels = levels;
              });
            },
            // Set selected tags list (복수 선택)
            setSelectedTagsList: (tags: string[]) => {
              set((state) => {
                state.selectedTagsList = tags;
              });
            },
            // Set selected exclusion mode
            setSelectedExclusionMode: (mode: string) => {
              set((state) => {
                state.selectedExclusionMode = mode;
              });
            },
            // Set selected count
            setSelectedCount: (count: number) => {
              set((state) => {
                state.selectedCount = count;
              });
            },

            // Set recommendation problems
            setProblems: (problems: RecommendedProblems[]) => {
              set((state) => {
                state.problems = problems;
              });
            },

            // Set loading state
            setLoading: (isLoading: boolean) => {
              set((state) => {
                state.isLoading = isLoading;
              });
            },

            // Set error state
            setError: (error: Error | null) => {
              set((state) => {
                state.error = error;
              });
            },

            // Toggle display filter
            toggleFilter: (filterName: keyof State['showFilters']) => {
              set((state) => {
                state.showFilters[filterName] = !state.showFilters[filterName];
              });
            },

            // Reset filters to initial state
            resetFilters: () => {
              set((state) => {
                state.showFilters = {
                  problemNumber: true,
                  problemTier: true,
                  recommendReason: true,
                  algorithm: false,
                };
              });
            },

            // Toggle section visibility
            toggleLevelSection: () => {
              set((state) => {
                state.showLevelSection = !state.showLevelSection;
                state.showFilterSection = false;
                state.showExcludedModeSection = false;
              });
            },

            toggleTagSection: () => {
              set((state) => {
                state.showTagSection = !state.showTagSection;
              });
            },

            toggleFilterSection: () => {
              set((state) => {
                state.showFilterSection = !state.showFilterSection;
                state.showLevelSection = false;
                state.showExcludedModeSection = false;
              });
            },
            toggleExcludedModeSection: () => {
              set((state) => {
                state.showExcludedModeSection = !state.showExcludedModeSection;
                state.showLevelSection = false;
                state.showFilterSection = false;
              });
            },
            // Clear recommendation
            clearRecommendation: () => {
              set((state) => {
                state.problems = [];
                state.isLoading = false;
                state.error = null;
              });
            },

            // Add recommendation to history
            addRecommendationHistory: (problems: RecommendedProblems[]) => {
              set((state) => {
                state.recommendationHistory.unshift({
                  timestamp: Date.now(),
                  problems,
                });
                // Keep only last 50 records
                if (state.recommendationHistory.length > 50) {
                  state.recommendationHistory = state.recommendationHistory.slice(0, 50);
                }
              });
            },

            // Clear recommendation history
            clearRecommendationHistory: () => {
              set((state) => {
                state.recommendationHistory = [];
              });
            },

            // Reset all state
            reset: () => {
              set(initialState);
            },
          },
        })),
      ),
      {
        name: 'recommendation-storage',
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
          recommendationHistory: state.recommendationHistory,
        }),
      },
    ),
    { name: 'RecommendationStore' },
  ),
);

// Selectors
export const useRecommendationStore = () => {
  const store = recommendationStoreInternal();
  return store as typeof store & State;
};

export const useSetSelectedLevels = () => {
  const setSelectedLevels = recommendationStoreInternal((s) => s.actions.setSelectedLevels);
  return setSelectedLevels;
};

export const useSetSelectedTagsList = () => {
  const setSelectedTagsList = recommendationStoreInternal((s) => s.actions.setSelectedTagsList);
  return setSelectedTagsList;
};

export const useSetSelectedExclusionMode = () => {
  const setSelectedExclusionMode = recommendationStoreInternal((s) => s.actions.setSelectedExclusionMode);
  return setSelectedExclusionMode;
};

export const useSetSelectedCount = () => {
  const setSelectedCount = recommendationStoreInternal((s) => s.actions.setSelectedCount);
  return setSelectedCount;
};

export const useSetProblems = () => {
  const setProblems = recommendationStoreInternal((s) => s.actions.setProblems);
  return setProblems;
};

export const useSetLoading = () => {
  const setLoading = recommendationStoreInternal((s) => s.actions.setLoading);
  return setLoading;
};

export const useSetError = () => {
  const setError = recommendationStoreInternal((s) => s.actions.setError);
  return setError;
};

export const useToggleFilter = () => {
  const toggleFilter = recommendationStoreInternal((s) => s.actions.toggleFilter);
  return toggleFilter;
};

export const useClearRecommendation = () => {
  const clearRecommendation = recommendationStoreInternal((s) => s.actions.clearRecommendation);
  return clearRecommendation;
};

export const useResetRecommendation = () => {
  const reset = recommendationStoreInternal((s) => s.actions.reset);
  return reset;
};
