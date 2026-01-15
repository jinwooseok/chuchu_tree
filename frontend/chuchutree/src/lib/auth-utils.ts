// src/lib/auth-utils.ts

/**
 * 토큰 재발급을 시도하는 공통 유틸 함수
 */
export async function refreshAccessToken(
  refreshToken: string,
  apiUrl: string = ''
): Promise<{ success: boolean; newCookies?: string }> {
  try {
    const refreshUrl = apiUrl
      ? `${apiUrl}/api/v1/auth/token/refresh`
      : '/api/v1/auth/token/refresh';

    const refreshResponse = await fetch(refreshUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Cookie: `refresh_token=${refreshToken}`,
      },
    });

    if (refreshResponse.ok) {
      // Set-Cookie 헤더에서 새 토큰 추출
      const setCookieHeader = refreshResponse.headers.get('set-cookie');

      if (setCookieHeader) {
        const newCookies = setCookieHeader
          .split(',')
          .map((cookie) => cookie.trim().split(';')[0])
          .join('; ');

        return { success: true, newCookies };
      }

      return { success: true };
    }

    return { success: false };
  } catch (error) {
    console.error('[refreshAccessToken] Error:', error);
    return { success: false };
  }
}

/**
 * 쿠키 파싱 유틸 (Middleware용)
 */
export function parseCookiesForMiddleware(setCookieHeader: string) {
  const cookieOptions: Record<string, any> = {};
  const cookies = setCookieHeader.split(',').map((c) => c.trim());

  return cookies.map((cookie) => {
    const [nameValue, ...attributes] = cookie.split(';');
    const [name, value] = nameValue.split('=');

    if (!name || !value) return null;

    const options: any = {};
    attributes.forEach((attr) => {
      const [key, val] = attr.trim().split('=');
      if (key.toLowerCase() === 'path') options.path = val;
      if (key.toLowerCase() === 'httponly') options.httpOnly = true;
      if (key.toLowerCase() === 'secure') options.secure = true;
      if (key.toLowerCase() === 'samesite') options.sameSite = val?.toLowerCase();
    });

    return { name, value, options };
  }).filter(Boolean);
}
