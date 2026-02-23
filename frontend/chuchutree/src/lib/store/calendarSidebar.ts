import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';

interface CalendarSidebarStore {
  showFilters: {
    algorithm: boolean;
    problemTier: boolean;
    problemNumber: boolean;
  };
  toggleFilter: (key: keyof CalendarSidebarStore['showFilters']) => void;
  resetFilters: () => void;
}

const initialFilters = {
  algorithm: true,
  problemTier: true,
  problemNumber: true,
};

export const useCalendarSidebarStore = create<CalendarSidebarStore>()(
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
      { name: 'calendar-sidebar-storage' },
    ),
    { name: 'CalendarSidebarStore' },
  ),
);
