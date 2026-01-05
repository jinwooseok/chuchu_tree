import { redirect } from 'next/navigation';
import { isAuthenticated, ApiResponseError } from '@/lib/server';
import { userServerApi } from '@/entities/user/api/user.server';
import { MainLayoutClient } from './MainLayoutClient';

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

  // 2단계: 사용자 정보 fetch
  let initialUserData = null;

  try {
    console.log('[MainLayout] Fetching user data...');
    initialUserData = await userServerApi.getMe();
    console.log('[MainLayout] User data fetched successfully:', {
      userAccountId: initialUserData?.userAccount?.userAccountId,
      bjAccountId: initialUserData?.bjAccount?.bjAccountId,
    });
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

  // initialUserData가 null이면 에러 (여기까지 왔으면 무조건 있어야 함)
  if (!initialUserData) {
    console.error('[MainLayout] User data is null, redirecting to sign-in');
    redirect('/sign-in');
  }

  return <MainLayoutClient initialUserData={initialUserData}>{children}</MainLayoutClient>;
}
