import axios from 'axios';

// 빈 문자열이면 상대 경로 사용 (프록시 모드)
const API_URL = process.env.NEXT_PUBLIC_API_URL || '';

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
  (error) => {
    return Promise.reject(error);
  },
);

// 응답 인터셉터 (401 처리 + RTR)
axiosInstance.interceptors.response.use(
  (response) => {
    // 성공 응답 그대로 반환
    return response;
  },
  async (error) => {
    const originalRequest = error.config;

    // 401 에러이고, 재시도하지 않은 요청인 경우
    if (error.response?.status === 401 && !originalRequest._retry && !originalRequest.url?.includes('/login')) {
      originalRequest._retry = true;

      try {
        // Refresh 토큰으로 새 Access 토큰 발급
        const refreshUrl = API_URL ? `${API_URL}/api/v1/auth/token/refresh` : '/api/v1/auth/token/refresh';
        await axios.post(refreshUrl, {}, { withCredentials: true });

        // 원래 요청 재시도
        return axiosInstance(originalRequest);
      } catch (refreshError) {
        // Refresh 실패 시 로그인 페이지로 리다이렉트
        if (typeof window !== 'undefined') {
          window.location.href = '/login';
        }
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  },
);
