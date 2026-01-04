import { cookies } from 'next/headers';
import { ApiResponse } from '@/shared/types/api';

const API_URL = process.env.NEXT_PUBLIC_API_URL!;

// 서버 컴포넌트용 공통 fetch 함수
export async function serverFetch<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const cookieStore = await cookies();

  // access_token과 refresh_token 모두 가져오기
  const accessToken = cookieStore.get('access_token')?.value;
  const refreshToken = cookieStore.get('refresh_token')?.value;

  // 쿠키 문자열 올바르게 구성 (세미콜론으로 구분)
  const cookieString = [accessToken && `access_token=${accessToken}`, refreshToken && `refresh_token=${refreshToken}`].filter(Boolean).join('; ');

  const response = await fetch(`${API_URL}/api/v1/${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
      ...(cookieString && { Cookie: cookieString }), // 쿠키가 있을 때만 헤더 추가
    },
    cache: options?.cache || 'no-store', // 기본값: SSR
  });

  // 에러 처리 개선
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(`API Error: ${response.status} - ${errorData.message || response.statusText}`);
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
