import { isAuthenticated } from '@/lib/server';
import { redirect } from 'next/navigation';
import DashboardLayout from './DashboardLayout';

export default async function HomePage() {
  // 인증 체크
  const isLoggedIn = await isAuthenticated();

  // 로그인 안 된 경우 로그인 페이지로 리다이렉트
  // if (!isLoggedIn) {
  //   redirect('/sign-in');
  // }

  return <DashboardLayout />;
}
