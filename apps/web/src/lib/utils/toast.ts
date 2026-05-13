/**
 * Toast 알림 유틸리티 함수
 * sonner 라이브러리의 toast를 래핑하여 공통 옵션을 적용합니다.
 */

import { toast as sonnerToast } from 'sonner';

/**
 * 공통 Toast 함수 모음
 * 모든 toast 호출에 position: 'top-center' 옵션이 자동으로 적용됩니다.
 */
export const toast = {
  /**
   * 성공 메시지 표시
   * @param message - 표시할 메시지
   */
  success: (message: string) => sonnerToast.success(message, { position: 'top-center' }),

  /**
   * 에러 메시지 표시
   * @param message - 표시할 메시지
   */
  error: (message: string) => sonnerToast.error(message, { position: 'top-center' }),

  /**
   * 정보 메시지 표시
   * @param message - 표시할 메시지
   */
  info: (message: string) => sonnerToast.info(message, { position: 'top-center' }),

  /**
   * 경고 메시지 표시
   * @param message - 표시할 메시지
   */
  warning: (message: string) => sonnerToast.warning(message, { position: 'top-center' }),
};
