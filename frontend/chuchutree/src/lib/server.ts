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

  let cookieString = [
    accessToken && `access_token=${accessToken}`,
    refreshToken && `refresh_token=${refreshToken}`
  ].filter(Boolean).join('; ');

  const requestUrl = `${API_URL}/api/v1/${endpoint}`;

  let response = await fetch(requestUrl, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
      ...(cookieString && { Cookie: cookieString }),
    },
    cache: options?.cache || 'no-store',
  });

  // 401 에러 처리
  if (response.status === 401 && refreshToken) {
    const errorData: ApiResponse<any> = await response.json().catch(() => ({}));

    if (errorData.error?.code === 'EXPIRED_TOKEN') {
      // 공통 함수 사용
      const { success, newCookies } = await refreshAccessToken(refreshToken, API_URL);

      if (success && newCookies) {
        cookieString = newCookies;

        // 원래 요청 재시도
        response = await fetch(requestUrl, {
          ...options,
          headers: {
            'Content-Type': 'application/json',
            ...options?.headers,
            Cookie: cookieString,
          },
          cache: options?.cache || 'no-store',
        });
      } else {
        throw new ApiResponseError(401, 'REFRESH_FAILED', 'Token refresh failed');
      }
    }
  }

  if (!response.ok) {
    const errorData: ApiResponse<any> = await response.json().catch(() => ({}));
    throw new ApiResponseError(
      response.status,
      errorData.error?.code,
      errorData.error?.message || errorData.message
    );
  }

  const result: ApiResponse<T> = await response.json();
  return result.data;
}


// 인증 여부 확인 헬퍼 함수
export async function isAuthenticated(): Promise<boolean> {
  const cookieStore = await cookies();
  const accessToken = cookieStore.get('access_token')?.value;
  return !!accessToken;
}

// 쿠키 가져오기 헬퍼 함수
export async function getAuthTokens() {
  const cookieStore = await cookies();
  return {
    accessToken: cookieStore.get('access_token')?.value,
    refreshToken: cookieStore.get('refresh_token')?.value,
  };
}
