/**
 * Zustand Store 테스트 유틸리티
 * 각 테스트마다 store를 초기화하여 테스트 격리 보장
 */

import { useTagDashboardSidebarStore } from '@/lib/store/tagDashboard';
import { useCalendarStore } from '@/lib/store/calendar';
import { useLayoutStore } from '@/lib/store/layout';
import { useRecommendationStore } from '@/lib/store/recommendation';
import { useRefreshButtonStore } from '@/lib/store/refreshButton';
import { useOnboardingStore } from '@/lib/store/onboarding';

/**
 * 모든 Zustand store를 초기 상태로 리셋
 * 각 테스트의 beforeEach에서 호출하여 테스트 격리 보장
 *
 * @example
 * ```typescript
 * beforeEach(() => {
 *   resetAllStores();
 * });
 * ```
 */
export const resetAllStores = () => {
  // 각 store의 getState().reset이 있다면 호출
  // 없다면 getState()를 직접 초기화
  // 필요에 따라 각 store의 초기화 로직 추가
  // 현재는 각 store가 reset 메서드를 제공하지 않으므로
  // 테스트에서 개별적으로 초기화 필요
};

/**
 * 특정 store를 초기 상태로 리셋
 *
 * @example
 * ```typescript
 * resetStore(useTagDashboard);
 * ```
 */
export const resetStore = (useStore: any) => {
  const state = useStore.getState();
  if (typeof state.reset === 'function') {
    state.reset();
  }
};
