import { redirect } from 'next/navigation';
import { isAuthenticated, ApiResponseError } from '@/lib/server';
import { MainLayoutClient } from './MainLayoutClient';
import { userServerApi } from '@/entities/user/api/user.server';
import { calendarServerApi } from '@/entities/calendar/api/calendar.server';
import { TagDashboardServerApi } from '@/entities/tag-dashboard/api/tagDashboard.server';
import { HydrationBoundary, QueryClient, dehydrate } from '@tanstack/react-query';
import { userKeys } from '@/entities/user/model/keys';
import { calendarKeys } from '@/entities/calendar/model/keys';
import { tagDashboardKeys } from '@/entities/tag-dashboard/model/keys';

export default async function MainLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  // 1단계: 인증 체크
  const isLoggedIn = await isAuthenticated();

  if (!isLoggedIn) {
    console.log('[MainLayout] User not authenticated, redirecting to sign-in');
    redirect('/sign-in');
  }

  // QueryClient 생성
  const queryClient = new QueryClient();

  // 2단계: 사용자 정보 직접 호출 및 에러 처리
  try {
    console.log('[MainLayout] Fetching user data...');
    const userData = await userServerApi.getMe();

    // 성공하면 QueryClient에 수동으로 설정
    queryClient.setQueryData(userKeys.me(), userData);
    console.log('[MainLayout] User data fetched successfully');
  } catch (error) {
    // UNLINKED_USER 에러: 백준 계정 미등록 사용자
    if (error instanceof ApiResponseError && error.errorCode === 'UNLINKED_USER') {
      console.log('[MainLayout] User not linked to Baekjoon account, redirecting to registration page');
      redirect('/bj-account');
    }

    // 기타 에러 발생 시 로그인 페이지로
    console.error('[MainLayout] Failed to fetch user data:', {
      message: error instanceof Error ? error.message : 'Unknown error',
      errorCode: error instanceof ApiResponseError ? error.errorCode : undefined,
    });
    redirect('/sign-in');
  }

  // 3단계: 오늘 날짜 기준 calendar 데이터 prefetch
  const today = new Date();
  const year = today.getFullYear();
  const month = today.getMonth() + 1; // 0-based → 1-based

  try {
    console.log('[MainLayout] Prefetching calendar data...', { year, month });
    await queryClient.prefetchQuery({
      queryKey: calendarKeys.list(year, month),
      queryFn: () => calendarServerApi.getCalendar({ year, month }),
    });
    console.log('[MainLayout] Calendar data prefetched successfully');
  } catch (error) {
    console.error('[MainLayout] Failed to prefetch calendar data:', {
      message: error instanceof Error ? error.message : 'Unknown error',
      errorCode: error instanceof ApiResponseError ? error.errorCode : undefined,
    });
    // Calendar 데이터는 선택적이므로 prefetch 실패해도 계속 진행
  }

  // 4단계: TagDashboard 데이터 prefetch
  try {
    console.log('[MainLayout] Prefetching TagDashboard...');
    await queryClient.prefetchQuery({
      queryKey: tagDashboardKeys.dashboard(),
      queryFn: TagDashboardServerApi.getTagDashboard,
    });
    console.log('[MainLayout] TagDashboard data prefetched successfully');
  } catch (error) {
    console.error('[MainLayout] Failed to prefetch TagDashboard data:', {
      message: error instanceof Error ? error.message : 'Unknown error',
      errorCode: error instanceof ApiResponseError ? error.errorCode : undefined,
    });
    // TagDashboard 데이터는 선택적이므로 prefetch 실패해도 계속 진행
  }

  return (
    <HydrationBoundary state={dehydrate(queryClient)}>
      <MainLayoutClient>{children}</MainLayoutClient>
    </HydrationBoundary>
  );
}
