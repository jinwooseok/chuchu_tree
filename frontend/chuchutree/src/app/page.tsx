import { redirect } from 'next/navigation';
import { isAuthenticated } from '@/lib/server';
import LandingPageClient from './LandingPageClient';

export default async function LandingPage() {
  // 로그인된 사용자는 "/chu"로 리다이렉트
  const isLoggedIn = await isAuthenticated();

  if (isLoggedIn) {
    redirect('/chu');
  }

  return <LandingPageClient />;
}
