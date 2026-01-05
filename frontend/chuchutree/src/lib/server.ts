import { cookies } from 'next/headers';
import { ApiResponse, ApiError } from '@/shared/types/api';

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

  // access_token과 refresh_token 모두 가져오기
  const accessToken = cookieStore.get('access_token')?.value;
  const refreshToken = cookieStore.get('refresh_token')?.value;

  // 쿠키 문자열 올바르게 구성 (세미콜론으로 구분)
  const cookieString = [accessToken && `access_token=${accessToken}`, refreshToken && `refresh_token=${refreshToken}`].filter(Boolean).join('; ');

  const requestUrl = `${API_URL}/api/v1/${endpoint}`;

  console.log('[serverFetch] Request:', {
    url: requestUrl,
    hasCookies: !!cookieString,
    hasAccessToken: !!accessToken,
    hasRefreshToken: !!refreshToken,
  });

  const response = await fetch(requestUrl, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
      ...(cookieString && { Cookie: cookieString }), // 쿠키가 있을 때만 헤더 추가
    },
    cache: options?.cache || 'no-store', // 기본값: SSR
  });

  console.log('[serverFetch] Response:', {
    url: requestUrl,
    status: response.status,
    statusText: response.statusText,
    ok: response.ok,
  });

  // 에러 처리 개선
  if (!response.ok) {
    const errorData: ApiResponse<any> = await response.json().catch(() => ({
      status: response.status,
      message: response.statusText,
      data: null,
      error: {},
    }));

    console.error('[serverFetch] Error response:', {
      url: requestUrl,
      status: response.status,
      errorData,
    });

    // 에러 코드와 메시지를 포함한 커스텀 에러 던지기
    throw new ApiResponseError(response.status, errorData.error?.code, errorData.error?.message || errorData.message);
  }

  // 응답 구조 처리
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
