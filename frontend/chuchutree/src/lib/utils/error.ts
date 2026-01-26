/**
 * API 에러 처리 유틸리티 함수
 */

import { AxiosError } from 'axios';

/**
 * API 에러 응답 타입
 */
interface ApiErrorResponse {
  error?: {
    code?: string;
    message?: string;
  };
}

/**
 * AxiosError에서 에러 메시지를 추출합니다.
 * @param error - 처리할 에러 객체
 * @param defaultMessage - 에러 메시지가 없을 때 사용할 기본 메시지
 * @returns 추출된 에러 메시지 또는 기본 메시지
 * @example
 * const errorMessage = getErrorMessage(error, '오류가 발생했습니다.');
 */
export const getErrorMessage = (error: unknown, defaultMessage = '오류가 발생했습니다.'): string => {
  if (error instanceof AxiosError) {
    const apiError = error.response?.data as ApiErrorResponse | undefined;
    return apiError?.error?.message || defaultMessage;
  }
  return defaultMessage;
};

/**
 * AxiosError에서 에러 코드를 추출합니다.
 * @param error - 처리할 에러 객체
 * @returns 에러 코드 또는 undefined
 * @example
 * const errorCode = getErrorCode(error);
 * if (errorCode === 'ALREADY_SOLVED_PROBLEM') {
 *   // 특정 에러 코드에 대한 처리
 * }
 */
export const getErrorCode = (error: unknown): string | undefined => {
  if (error instanceof AxiosError) {
    const apiError = error.response?.data as ApiErrorResponse | undefined;
    return apiError?.error?.code;
  }
  return undefined;
};
