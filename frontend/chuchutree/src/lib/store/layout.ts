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

  // 액션들
  setTopSection: (section: TopSection) => void;
  toggleTopSection: (section: 'tierbar' | 'streak') => void;
  setCenterSection: (section: CenterSection) => void;
  toggleBottomSection: () => void;
  setInfoSidebarWidth: () => void;
  setTopSectionTierbarHeight: () => void;
  setTopSectionStreakHeight: () => void;
  setBottomSectionHeight: () => void;
}

export const useLayoutStore = create<LayoutState>()(
  devtools(
    persist(
      immer((set) => ({
        // 초기 상태
        topSection: null,
        centerSection: 'calendar',
        bottomSection: null,
        infoSidebarWidth: 200,
        topSectionTierbarHeight: 80,
        topSectionStreakHeight: 240,
        bottomSectionHeight: 240,

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

        // 티어바 높이 조절
        setTopSectionTierbarHeight: () => {
          set((state) => {
            state.topSectionTierbarHeight = 60;
          });
        },
        // 스트릭바 높이 조절
        setTopSectionStreakHeight: () => {
          set((state) => {
            state.topSectionStreakHeight = 60;
          });
        },
        // 하단 추천 높이 조절
        setBottomSectionHeight: () => {
          set((state) => {
            state.bottomSectionHeight = 60;
          });
        },
        setInfoSidebarWidth: () => {
          set((state) => {
            state.infoSidebarWidth = 300;
          });
        },
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
