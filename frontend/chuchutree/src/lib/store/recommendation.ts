import { create } from 'zustand';
import { combine, devtools, persist } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';

type LevelType = 'easy' | 'normal' | 'hard' | 'extreme';

interface RecommendedProblems {
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

type State = {
  // Filter state
  selectedLevel: LevelType | null;
  selectedTags: string;

  // Recommendation result
  problems: RecommendedProblems[];
  isLoading: boolean;
  error: Error | null;

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
};

const initialState: State = {
  selectedLevel: null,
  selectedTags: '',
  problems: [],
  isLoading: false,
  error: null,
  showFilters: {
    problemNumber: true,
    problemTier: true,
    recommendReason: true,
    algorithm: false,
  },
  showLevelSection: false,
  showTagSection: false,
  showFilterSection: false,
};

const recommendationStoreInternal = create(
  devtools(
    persist(
      immer(
        combine(initialState, (set, get) => ({
          actions: {
            // Set selected level
            setSelectedLevel: (level: LevelType | null) => {
              set((state) => {
                state.selectedLevel = level;
              });
            },

            // Set selected tags
            setSelectedTags: (tags: string) => {
              set((state) => {
                state.selectedTags = tags;
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
          selectedLevel: state.selectedLevel,
          selectedTags: state.selectedTags,
          showFilters: state.showFilters,
          showLevelSection: state.showLevelSection,
          showTagSection: state.showTagSection,
          showFilterSection: state.showFilterSection,
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

export const useSetSelectedLevel = () => {
  const setSelectedLevel = recommendationStoreInternal((s) => s.actions.setSelectedLevel);
  return setSelectedLevel;
};

export const useSetSelectedTags = () => {
  const setSelectedTags = recommendationStoreInternal((s) => s.actions.setSelectedTags);
  return setSelectedTags;
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
