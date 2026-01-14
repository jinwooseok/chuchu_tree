import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';
import { refreshAccessToken, parseCookiesForMiddleware } from '@/lib/auth-utils';

// 인증이 필요한 경로
const protectedPaths = ['/', '/bj-account'];

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const accessToken = request.cookies.get('access_token')?.value;
  const refreshToken = request.cookies.get('refresh_token')?.value;

  if (protectedPaths.includes(pathname)) {
    if (!accessToken) {
      return NextResponse.redirect(new URL('/sign-in', request.url));
    }
    // access_token이 있는 경우, 유효성 검증
    // local환경: rewrites에 의해 https://chuchu-tree-dev.duckdns.org/api/v1/bj-accounts/me로 프록시
    // 배포 dev 환경: 상대 경로이므로 현재 도메인 기준 https://chuchu-tree-dev.duckdns.org/api/v1/bj-accounts/me 요청 후 Nginx가 이를 FastAPI:8002로 라우팅
    // 배포 production 환경: 상대 경로이므로 https://chuchu-tree.duckdns.org/api/v1/bj-accounts/me 요청 후 Nginx가 FastAPI로 FastAPI:8001(추정)로 라우팅
    try {
      const verifyResponse = await fetch(`/api/v1/bj-accounts/me`, {
        headers: {
          Cookie: `access_token=${accessToken}${refreshToken ? `; refresh_token=${refreshToken}` : ''}`,
        },
      });

      if (verifyResponse.ok) {
        return NextResponse.next();
      }

      // 401 에러 - 토큰 만료
      if (verifyResponse.status === 401 && refreshToken) {
        // 공통 함수 사용
        const { success, newCookies } = await refreshAccessToken(refreshToken, '');

        if (success && newCookies) {
          const response = NextResponse.next();
          const cookies = parseCookiesForMiddleware(newCookies);

          cookies.forEach((cookie) => {
            if (cookie) {
              response.cookies.set(cookie.name, cookie.value, cookie.options);
            }
          });

          return response;
        }
      }

      // 재발급 실패
      const response = NextResponse.redirect(new URL('/sign-in', request.url));
      response.cookies.delete('access_token');
      response.cookies.delete('refresh_token');
      return response;
    } catch (error) {
      console.error('[Middleware] Error:', error);
      return NextResponse.next();
    }
  }

  return NextResponse.next();
}

// middleware가 실행될 경로 설정
export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     */
    '/((?!api|_next/static|_next/image|favicon.ico).*)',
  ],
};
