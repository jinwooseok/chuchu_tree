import { create } from 'zustand';
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

  // 액션들
  setTopSection: (section: TopSection) => void;
  toggleTopSection: (section: 'tierbar' | 'streak') => void;
  setCenterSection: (section: CenterSection) => void;
  toggleBottomSection: () => void;
}

export const useLayoutStore = create<LayoutState>()(
  immer((set) => ({
    // 초기 상태
    topSection: null,
    centerSection: 'calendar', // 기본값: 캘린더
    bottomSection: null,

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
          // 다른 버튼 클릭 시 변경
          state.topSection = section;
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
        state.bottomSection = state.bottomSection === 'recommend' ? null : 'recommend';
      }),
  })),
);
