import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';
import type { ApiError } from '@/shared/types/api';

// 빈 문자열이면 상대 경로 사용 (프록시 모드)
const API_URL = process.env.NEXT_PUBLIC_API_URL || '';

// _retry 속성을 포함한 config 타입
interface CustomAxiosRequestConfig extends InternalAxiosRequestConfig {
  _retry?: boolean;
}

// 기본 Axios 인스턴스
export const axiosInstance = axios.create({
  baseURL: API_URL ? `${API_URL}/api/v1` : '/api/v1',
  timeout: 10000,
  withCredentials: true, // credentials: 'include' 역할
  headers: {
    'Content-Type': 'application/json',
  },
});

// 요청 인터셉터
axiosInstance.interceptors.request.use(
  (config) => {
    return config;
  },
  (error: AxiosError<ApiError>) => {
    return Promise.reject(error);
  },
);

axiosInstance.interceptors.response.use(
  (response) => response,
  async (error: AxiosError<ApiError>) => {
    const originalRequest = error.config as CustomAxiosRequestConfig;

    if (
      error.response?.status === 401 &&
      !originalRequest._retry &&
      !originalRequest.url?.includes('/sign-in')
    ) {
      originalRequest._retry = true;

      try {
        const API_URL = process.env.NEXT_PUBLIC_API_URL || '';

        // 공통 함수 사용 (간단한 버전)
        await axios.post(
          API_URL ? `${API_URL}/api/v1/auth/token/refresh` : '/api/v1/auth/token/refresh',
          {},
          { withCredentials: true }
        );

        return axiosInstance(originalRequest);
      } catch (refreshError: unknown) {
        if (typeof window !== 'undefined') {
          window.location.href = '/sign-in';
        }
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

