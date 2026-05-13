/**
 * React Query 테스트 유틸리티
 * 테스트에서 React Query를 사용할 수 있도록 QueryClientProvider wrapper 제공
 */

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactNode } from 'react';

/**
 * 테스트용 QueryClient 생성
 * retry를 비활성화하여 테스트 속도 향상
 */
export const createTestQueryClient = () =>
  new QueryClient({
    defaultOptions: {
      queries: {
        retry: false, // 테스트에서는 재시도 비활성화
        gcTime: Infinity, // 가비지 컬렉션 타임 무한대
      },
      mutations: {
        retry: false,
      },
    },
  });

/**
 * React Query wrapper 컴포넌트
 * renderHook이나 render에서 wrapper로 사용
 *
 * @example
 * ```typescript
 * const { result } = renderHook(() => useMyQuery(), { wrapper });
 * ```
 */
export function QueryWrapper({ children }: { children: ReactNode }) {
  const queryClient = createTestQueryClient();
  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
}
