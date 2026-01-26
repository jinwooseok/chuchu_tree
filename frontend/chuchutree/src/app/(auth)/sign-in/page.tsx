import { redirect } from 'next/navigation';
import { isAuthenticated } from '@/lib/server';
import SignInClient from './SignInClient';

export default async function SignIn() {
  // 로그인된 사용자는 홈으로 리다이렉트
  const isLoggedIn = await isAuthenticated();

  if (isLoggedIn) {
    redirect('/');
  }

  return <SignInClient />;
}
