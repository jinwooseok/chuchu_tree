import { userServerApi } from '@/entities/user/api/user.server';
import { isAuthenticated } from '@/lib/server';
import { redirect } from 'next/navigation';

export default async function HomePage() {
  // 인증 체크
  const isLoggedIn = await isAuthenticated();

  // 로그인 안 된 경우 로그인 페이지로 리다이렉트
  // if (!isLoggedIn) {
  //   redirect('/sign-in');
  // }

  // 로그인한 경우에만 사용자 데이터 가져오기
  const user = isLoggedIn ? await userServerApi.getMe() : null;

  return <div>메인</div>;
}
