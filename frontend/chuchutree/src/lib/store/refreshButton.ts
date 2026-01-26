import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';

interface RefreshButtonState {
  isRefreshButtonVisible: boolean;
  hideRefreshButton: () => void;
  showRefreshButton: () => void;
}

export const useRefreshButtonStore = create<RefreshButtonState>()(
  devtools(
    persist(
      immer((set) => ({
        // 초기 상태
        isRefreshButtonVisible: true,

        // RefreshButton 숨기기
        hideRefreshButton: () =>
          set((state) => {
            state.isRefreshButtonVisible = false;
          }),

        // RefreshButton 보이기
        showRefreshButton: () =>
          set((state) => {
            state.isRefreshButtonVisible = true;
          }),
      })),
      {
        name: 'refresh-button-storage',
        partialize: (state) => ({
          isRefreshButtonVisible: state.isRefreshButtonVisible,
        }),
      },
    ),
    { name: 'RefreshButtonStore' },
  ),
);
