import { UserProfile } from '@/entities/user';
import { userServerApi } from '@/entities/user/api/user.server';
import { isAuthenticated } from '@/lib/server';

export default async function HomePage() {
  // 인증 체크
  const isLoggedIn = await isAuthenticated();

  // 로그인한 경우에만 사용자 데이터 가져오기
  const user = isLoggedIn ? await userServerApi.getMe() : null;

  return (
    <div>
      {isLoggedIn && user ? (
        <>
          <h1>환영합니다, {user.username}님</h1>
          <UserProfile />
        </>
      ) : (
        <>
          <h1>ChuChuTree에 오신 것을 환영합니다</h1>
          <p>로그인하여 알고리즘 학습을 시작하세요!</p>
          <a href="/login">로그인하기</a>
        </>
      )}
    </div>
  );
}
