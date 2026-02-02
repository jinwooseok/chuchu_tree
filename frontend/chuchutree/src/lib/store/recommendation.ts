import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';

export interface RecommendedProblems {
  problemId: number;
  problemTitle: string;
  problemTierLevel: number;
  problemTierName: string;
  problemClassLevel: number;
  recommandReasons: {
    reason: string;
    additionalData: string | null;
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

interface RecommendationStore {
  // Filter state
  selectedLevels: string[];
  selectedTagsList: string[];
  selectedExclusionMode: string;
  selectedCount: number;

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

  // Actions
  setSelectedLevels: (levels: string[]) => void;
  setSelectedTagsList: (tags: string[]) => void;
  setSelectedExclusionMode: (mode: string) => void;
  setSelectedCount: (count: number) => void;
  setProblems: (problems: RecommendedProblems[]) => void;
  setLoading: (isLoading: boolean) => void;
  setError: (error: Error | null) => void;
  toggleFilter: (filterName: keyof RecommendationStore['showFilters']) => void;
  resetFilters: () => void;
  toggleLevelSection: () => void;
  toggleTagSection: () => void;
  toggleFilterSection: () => void;
  toggleExcludedModeSection: () => void;
  clearRecommendation: () => void;
  addRecommendationHistory: (problems: RecommendedProblems[]) => void;
  clearRecommendationHistory: () => void;
  reset: () => void;
}

const initialState = {
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

export const useRecommendationStore = create<RecommendationStore>()(
  devtools(
    persist(
      immer((set) => ({
        ...initialState,

        // Set selected levels
        setSelectedLevels: (levels: string[]) => {
          set((state) => {
            state.selectedLevels = levels;
          });
        },

        // Set selected tags list
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
        toggleFilter: (filterName) => {
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
      })),
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
