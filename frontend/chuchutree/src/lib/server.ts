import { cookies } from 'next/headers';
import { ApiResponse, ApiError } from '@/shared/types/api';
import { refreshAccessToken } from '@/lib/auth-utils';

// 커스텀 API 에러 클래스
export class ApiResponseError extends Error {
  constructor(
    public status: number,
    public errorCode?: string,
    public errorMessage?: string,
  ) {
    super(errorMessage || `API Error: ${status}`);
    this.name = 'ApiResponseError';
  }
}

// 서버에서는 프록시를 사용할 수 없으므로 직접 백엔드 URL 사용
const API_URL = process.env.NEXT_PUBLIC_BACKEND_URL || process.env.NEXT_PUBLIC_API_URL || 'https://chuchu-tree-dev.duckdns.org';

// 서버 컴포넌트용 공통 fetch 함수
export async function serverFetch<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const cookieStore = await cookies();
  const accessToken = cookieStore.get('access_token')?.value;
  const refreshToken = cookieStore.get('refresh_token')?.value;

  const cookieString = [accessToken && `access_token=${accessToken}`, refreshToken && `refresh_token=${refreshToken}`].filter(Boolean).join('; ');

  const requestUrl = `${API_URL}/api/v1/${endpoint}`;

  const response = await fetch(requestUrl, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
      ...(cookieString && { Cookie: cookieString }),
    },
    cache: options?.cache || 'no-store',
  });

  // 에러 처리 (401 재발급은 isAuthenticated()에서 처리)
  if (!response.ok) {
    const errorData: ApiResponse<any> = await response.json().catch(() => ({}));
    throw new ApiResponseError(response.status, errorData.error?.error?.code, errorData.error?.error?.message || errorData.message);
  }

  const result: ApiResponse<T> = await response.json();
  return result.data;
}

// 인증 여부 확인 헬퍼 함수 (토큰 검증 + 재발급)
export async function isAuthenticated(): Promise<boolean> {
  const cookieStore = await cookies();
  const accessToken = cookieStore.get('access_token')?.value;
  const refreshToken = cookieStore.get('refresh_token')?.value;

  // 1. 토큰이 없으면 false
  if (!accessToken) {
    console.log('[isAuthenticated] No access token');
    return false;
  }

  // 2. 토큰 유효성 검증
  const verifyUrl = `${API_URL}/api/v1/auth/me`;
  try {
    const verifyResponse = await fetch(verifyUrl, {
      headers: {
        Cookie: `access_token=${accessToken}${refreshToken ? `; refresh_token=${refreshToken}` : ''}`,
      },
    });

    // 3. 유효하면 true (404는 백준 미연동이지만 인증은 성공)
    if (verifyResponse.ok || verifyResponse.status === 404) {
      console.log('[isAuthenticated] Token valid, status:', verifyResponse.status);
      return true;
    }

    // 4. 401이면 재발급 시도
    if (verifyResponse.status === 401 && refreshToken) {
      console.log('[isAuthenticated] Token expired, attempting refresh');
      const { success } = await refreshAccessToken(refreshToken, API_URL);

      if (success) {
        console.log('[isAuthenticated] Token refresh successful');
      } else {
        console.log('[isAuthenticated] Token refresh failed');
      }

      return success;
    }

    // 5. 기타 에러
    console.log('[isAuthenticated] Verification failed, status:', verifyResponse.status);
    return false;
  } catch (error) {
    console.error('[isAuthenticated] Error during verification:', error);
    return false;
  }
}

// 쿠키 가져오기 헬퍼 함수
export async function getAuthTokens() {
  const cookieStore = await cookies();
  return {
    accessToken: cookieStore.get('access_token')?.value,
    refreshToken: cookieStore.get('refresh_token')?.value,
  };
}
