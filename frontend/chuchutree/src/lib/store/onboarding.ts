import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';

interface OnboardingState {
  // localStorage에 저장될 값 (완료 여부)
  hasCompletedOnboarding: boolean;
  // 세션 상태 (현재 온보딩 진행 중 여부)
  isActive: boolean;
  // 현재 단계
  currentStep: number;
  // hydration 완료 여부
  _hasHydrated: boolean;

  // 액션들
  startOnboarding: () => void;
  nextStep: () => void;
  skipCurrentStep: () => void; // 현재 step만 건너뛰고 다음으로
  completeOnboarding: () => void; // 온보딩 완전히 종료
  resetOnboarding: () => void;
  setHasHydrated: (state: boolean) => void;
}

export const useOnboardingStore = create<OnboardingState>()(
  devtools(
    persist(
      immer((set) => ({
        // 초기 상태
        hasCompletedOnboarding: false,
        isActive: false,
        currentStep: 1,
        _hasHydrated: false,

        // hydration 완료 설정
        setHasHydrated: (state: boolean) =>
          set((draft) => {
            draft._hasHydrated = state;
          }),

        // 온보딩 시작
        startOnboarding: () =>
          set((state) => {
            state.isActive = true;
            state.currentStep = 1;
          }),

        // 다음 단계로 이동
        nextStep: () =>
          set((state) => {
            state.currentStep += 1;
          }),

        // 현재 step만 건너뛰고 다음으로 (Step 9에서는 종료)
        skipCurrentStep: () =>
          set((state) => {
            if (state.currentStep >= 8) {
              // 마지막 step이면 온보딩 완료
              state.hasCompletedOnboarding = true;
              state.isActive = false;
              state.currentStep = 1;
            } else {
              // 다음 step으로 이동
              state.currentStep += 1;
            }
          }),

        // 온보딩 완료
        completeOnboarding: () =>
          set((state) => {
            state.hasCompletedOnboarding = true;
            state.isActive = false;
            state.currentStep = 1;
          }),

        // 재시작 (localStorage 초기화)
        resetOnboarding: () =>
          set((state) => {
            state.hasCompletedOnboarding = false;
            state.isActive = false;
            state.currentStep = 1;
          }),
      })),
      {
        name: 'onboarding-storage',
        // localStorage에는 완료 여부만 저장
        partialize: (state) => ({
          hasCompletedOnboarding: state.hasCompletedOnboarding,
        }),
        // hydration 완료 시 플래그 설정
        onRehydrateStorage: () => (state) => {
          state?.setHasHydrated(true);
        },
      },
    ),
    { name: 'OnboardingStore' },
  ),
);
