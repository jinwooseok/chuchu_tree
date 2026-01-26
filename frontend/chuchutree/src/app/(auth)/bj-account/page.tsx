import { redirect } from 'next/navigation';
import { isAuthenticated } from '@/lib/server';
import { userServerApi } from '@/entities/user/api/user.server';
import { ApiResponseError } from '@/lib/server';
import BjAccountRegistrationClient from './BjAccountRegistrationClient';
import { User } from '@/entities/user';

export default async function BjAccountRegistration() {
  // 1. 인증 체크
  const isLoggedIn = await isAuthenticated();

  if (!isLoggedIn) {
    redirect('/sign-in');
  }

  // 2. 사용자 정보 체크
  let userData: User | null = null;

  try {
    userData = await userServerApi.getMe();
  } catch (error) {
    // UNLINKED_USER 에러는 정상 (백준 계정 미등록 사용자)
    if (error instanceof ApiResponseError && error.errorCode === 'UNLINKED_USER') {
      // 계정 등록 페이지를 보여줌
      return <BjAccountRegistrationClient />;
    }

    // 기타 에러는 로그인 페이지로
    redirect('/sign-in');
  }

  // 이미 백준 계정이 등록되어 있으면 홈으로 리다이렉트
  if (userData?.bjAccount?.bjAccountId) {
    redirect('/chu');
  }

  return <BjAccountRegistrationClient />;
}
