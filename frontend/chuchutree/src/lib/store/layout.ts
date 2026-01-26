import { create } from 'zustand';
import { combine, devtools, persist } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';

// 상단 영역 타입 (티어바, 스트릭, 닫힘)
type TopSection = 'tierbar' | 'streak' | null;
// 중앙 영역 타입 (캘린더, 태그 대시보드)
type CenterSection = 'calendar' | 'dashboard';
// 하단 영역 타입 (문제추천, 닫힘)
type BottomSection = 'recommend' | null;

interface LayoutState {
  // 현재 보이는 영역들
  topSection: TopSection;
  centerSection: CenterSection;
  bottomSection: BottomSection;
  infoSidebarWidth: number;
  topSectionTierbarHeight: number;
  topSectionStreakHeight: number;
  bottomSectionHeight: number;
  isResizing: boolean;

  // 액션들
  setTopSection: (section: TopSection) => void;
  toggleTopSection: (section: 'tierbar' | 'streak') => void;
  setCenterSection: (section: CenterSection) => void;
  toggleBottomSection: () => void;
  setResizing: (isResizing: boolean) => void;
  setInfoSidebarWidth: (width: number) => void;
  setTopSectionTierbarHeight: (height: number) => void;
  setTopSectionStreakHeight: (height: number) => void;
  setBottomSectionHeight: (height: number) => void;
}

export const useLayoutStore = create<LayoutState>()(
  devtools(
    persist(
      immer((set) => ({
        // 초기 상태
        topSection: null,
        centerSection: 'calendar',
        bottomSection: null,
        infoSidebarWidth: 280,
        topSectionTierbarHeight: 120,
        topSectionStreakHeight: 240,
        bottomSectionHeight: 240,
        isResizing: false,

        // 상단 영역 직접 설정
        setTopSection: (section) =>
          set((state) => {
            state.topSection = section;
          }),

        // 상단 영역 토글 (티어바/스트릭/닫힘)
        toggleTopSection: (section) =>
          set((state) => {
            // 같은 버튼 클릭 시 닫기
            if (state.topSection === section) {
              state.topSection = null;
            } else {
              // 다른 버튼 클릭 시 변경 + 하단 영역 닫기
              state.topSection = section;
              state.bottomSection = null;
            }
          }),

        // 중앙 영역 설정 (캘린더 <-> 대시보드 토글)
        setCenterSection: (section) =>
          set((state) => {
            state.centerSection = section;
          }),

        // 하단 영역 토글 (문제추천 열기/닫기)
        toggleBottomSection: () =>
          set((state) => {
            if (state.bottomSection === 'recommend') {
              // 이미 열려있으면 닫기
              state.bottomSection = null;
            } else {
              // 닫혀있으면 열기 + 상단 영역 닫기
              state.bottomSection = 'recommend';
              state.topSection = null;
            }
          }),

        // 리사이즈 상태 설정
        setResizing: (isResizing) =>
          set((state) => {
            state.isResizing = isResizing;
          }),

        // InfoSidebar 너비 조절
        setInfoSidebarWidth: (width) =>
          set((state) => {
            state.infoSidebarWidth = width;
          }),

        // 티어바 높이 조절
        setTopSectionTierbarHeight: (height) =>
          set((state) => {
            state.topSectionTierbarHeight = height;
          }),

        // 스트릭바 높이 조절
        setTopSectionStreakHeight: (height) =>
          set((state) => {
            state.topSectionStreakHeight = height;
          }),

        // 하단 추천 높이 조절
        setBottomSectionHeight: (height) =>
          set((state) => {
            state.bottomSectionHeight = height;
          }),
      })),
      {
        name: 'layout-storage',
        partialize: (state) => ({
          topSection: state.topSection,
          centerSection: state.centerSection,
          bottomSection: state.bottomSection,
          infoSidebarWidth: state.infoSidebarWidth,
          topSectionTierbarHeight: state.topSectionTierbarHeight,
          topSectionStreakHeight: state.topSectionStreakHeight,
          bottomSectionHeight: state.bottomSectionHeight,
        }),
      },
    ),
    { name: 'LayoutStore' },
  ),
);
