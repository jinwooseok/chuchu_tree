import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

const API_URL = process.env.NEXT_PUBLIC_BACKEND_URL || process.env.NEXT_PUBLIC_API_URL || 'https://chuchu-tree-dev.duckdns.org';

// 인증이 필요한 경로
const protectedPaths = ['/', '/bj-account'];

const isDev = process.env.NODE_ENV === 'development';

// 인증된 사용자가 접근하면 안되는 경로
const authPaths = ['/sign-in'];

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const accessToken = request.cookies.get('access_token')?.value;
  const refreshToken = request.cookies.get('refresh_token')?.value;

  // console.log('[Middleware]', {
  //   pathname,
  //   hasAccessToken: !!accessToken,
  //   hasRefreshToken: !!refreshToken,
  // });

  // 보호된 경로에 대한 처리
  if (protectedPaths.includes(pathname)) {
    // 토큰이 아예 없으면 로그인 페이지로
    if (!accessToken) {
      console.log('[Middleware] No access token, redirecting to sign-in');
      return NextResponse.redirect(new URL('/sign-in', request.url));
    }

    // access_token이 있는 경우, 유효성 검증
    try {
      console.log('[T@KENCHECK]');
      const verifyResponse = await fetch(`${API_URL}/api/v1/bj-accounts/me`, {
        method: 'GET',
        headers: {
          Cookie: `access_token=${accessToken}${refreshToken ? `; refresh_token=${refreshToken}` : ''}`,
        },
      });

      // 토큰이 유효하면 통과
      if (verifyResponse.ok) {
        console.log('[Middleware] Token valid, allowing access');
        return NextResponse.next();
      }

      // 401 에러 - 토큰 만료
      if (verifyResponse.status === 401 && refreshToken) {
        console.log('[Middleware] Access token expired, attempting refresh');

        // Refresh token으로 재발급 시도
        const refreshResponse = await fetch(`${API_URL}/api/v1/auth/token/refresh`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Cookie: `refresh_token=${refreshToken}`,
          },
        });
        // Refresh token 재발급 성공
        if (refreshResponse.ok) {
          console.log('[Middleware] Token refresh successful');

          // 새 토큰을 쿠키에 설정
          const response = NextResponse.next();
          const setCookieHeader = refreshResponse.headers.get('set-cookie');

          if (setCookieHeader) {
            // Set-Cookie 헤더를 파싱하여 각각 설정
            const cookies = setCookieHeader.split(',').map((c) => c.trim());
            cookies.forEach((cookie) => {
              const [nameValue, ...attributes] = cookie.split(';');
              const [name, value] = nameValue.split('=');

              if (name && value) {
                // 쿠키 속성 파싱
                const cookieOptions: any = {};
                attributes.forEach((attr) => {
                  const [key, val] = attr.trim().split('=');
                  if (key.toLowerCase() === 'path') cookieOptions.path = val;
                  if (key.toLowerCase() === 'httponly') cookieOptions.httpOnly = true;
                  if (key.toLowerCase() === 'secure') cookieOptions.secure = true;
                  if (key.toLowerCase() === 'samesite') cookieOptions.sameSite = val?.toLowerCase();
                });

                response.cookies.set(name, value, cookieOptions);
              }
            });
          }
          return response;
        } else {
          console.log('[Middleware] Token refresh failed, clearing cookies');

          // Refresh 실패 - 쿠키 삭제 후 로그인 페이지로
          const response = NextResponse.redirect(new URL('/sign-in', request.url));
          response.cookies.delete('access_token');
          response.cookies.delete('refresh_token');
          return response;
        }
      }
      // 401이지만 refresh_token이 없거나, 다른 에러
      console.log('[Middleware] Authentication failed, clearing cookies');
      const response = NextResponse.redirect(new URL('/sign-in', request.url));
      response.cookies.delete('access_token');
      response.cookies.delete('refresh_token');
      return response;
    } catch (error) {
      console.error('[Middleware] Error during token validation:', error);
      if (isDev) {
        // dev에서는 그냥 통과 or 유지
        return NextResponse.next();
      }
      // 네트워크 에러 등 - 쿠키 삭제 후 로그인 페이지로
      const response = NextResponse.redirect(new URL('/sign-in', request.url));
      response.cookies.delete('access_token');
      response.cookies.delete('refresh_token');
      return response;
    }
  }

  // 인증 페이지 (로그인)에 대한 처리
  if (authPaths.includes(pathname)) {
    // 유효한 토큰이 있으면 홈으로 리다이렉트
    if (accessToken) {
      console.log('[Middleware] Already authenticated, redirecting to home');
      return NextResponse.redirect(new URL('/', request.url));
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
