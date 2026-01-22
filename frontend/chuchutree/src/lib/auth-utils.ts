// src/lib/auth-utils.ts

// 쿠키 옵션 타입 정의
interface CookieOptions {
  path?: string;
  httpOnly?: boolean;
  secure?: boolean;
  sameSite?: 'strict' | 'lax' | 'none';
}

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

// 파싱된 쿠키 타입 정의
interface ParsedCookie {
  name: string;
  value: string;
  options: CookieOptions;
}

/**
 * 쿠키 파싱 유틸 (Middleware용)
 */
export function parseCookiesForMiddleware(setCookieHeader: string): (ParsedCookie | null)[] {
  const cookies = setCookieHeader.split(',').map((c) => c.trim());

  return cookies.map((cookie) => {
    const [nameValue, ...attributes] = cookie.split(';');
    const [name, value] = nameValue.split('=');

    if (!name || !value) return null;

    const options: CookieOptions = {};
    attributes.forEach((attr) => {
      const [key, val] = attr.trim().split('=');
      const lowerKey = key.toLowerCase();

      if (lowerKey === 'path') {
        options.path = val;
      } else if (lowerKey === 'httponly') {
        options.httpOnly = true;
      } else if (lowerKey === 'secure') {
        options.secure = true;
      } else if (lowerKey === 'samesite') {
        const sameSiteValue = val?.toLowerCase();
        if (sameSiteValue === 'strict' || sameSiteValue === 'lax' || sameSiteValue === 'none') {
          options.sameSite = sameSiteValue;
        }
      }
    });

    return { name, value, options };
  }).filter(Boolean);
}
