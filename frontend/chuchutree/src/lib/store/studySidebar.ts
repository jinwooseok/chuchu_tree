import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';

interface StudySidebarStore {
  showFilters: {
    algorithm: boolean;
    problemTier: boolean;
    problemNumber: boolean;
  };
  toggleFilter: (key: keyof StudySidebarStore['showFilters']) => void;
  resetFilters: () => void;
}

const initialFilters = {
  algorithm: true,
  problemTier: true,
  problemNumber: true,
};

export const useStudySidebarStore = create<StudySidebarStore>()(
  devtools(
    persist(
      immer((set) => ({
        showFilters: { ...initialFilters },

        toggleFilter: (key) => {
          set((state) => {
            state.showFilters[key] = !state.showFilters[key];
          });
        },

        resetFilters: () => {
          set((state) => {
            state.showFilters = { ...initialFilters };
          });
        },
      })),
      { name: 'study-sidebar-storage' },
    ),
    { name: 'StudySidebarStore' },
  ),
);
