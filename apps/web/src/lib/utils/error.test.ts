/**
 * API 에러 처리 유틸리티 함수 테스트
 */

import { AxiosError } from 'axios';
import { getErrorMessage, getErrorCode } from './error';

describe('getErrorMessage', () => {
  it('AxiosError에서 에러 메시지를 추출한다', () => {
    const error = new AxiosError('Network Error');
    error.response = {
      data: {
        error: {
          message: 'API 오류 발생',
        },
      },
    } as any;

    expect(getErrorMessage(error)).toBe('API 오류 발생');
  });

  it('에러 메시지가 없으면 기본 메시지를 반환한다', () => {
    const error = new AxiosError('Network Error');
    error.response = {
      data: {},
    } as any;

    expect(getErrorMessage(error)).toBe('오류가 발생했습니다.');
  });

  it('커스텀 기본 메시지를 사용한다', () => {
    const error = new AxiosError('Network Error');
    error.response = {
      data: {},
    } as any;

    expect(getErrorMessage(error, '커스텀 에러 메시지')).toBe('커스텀 에러 메시지');
  });

  it('AxiosError가 아닌 경우 기본 메시지를 반환한다', () => {
    const error = new Error('일반 에러');
    expect(getErrorMessage(error)).toBe('오류가 발생했습니다.');
  });

  it('response가 없는 경우 기본 메시지를 반환한다', () => {
    const error = new AxiosError('Network Error');
    expect(getErrorMessage(error)).toBe('오류가 발생했습니다.');
  });

  it('error.data가 없는 경우 기본 메시지를 반환한다', () => {
    const error = new AxiosError('Network Error');
    error.response = {} as any;
    expect(getErrorMessage(error)).toBe('오류가 발생했습니다.');
  });

  it('error.error.message가 빈 문자열인 경우 기본 메시지를 반환한다', () => {
    const error = new AxiosError('Network Error');
    error.response = {
      data: {
        error: {
          message: '',
        },
      },
    } as any;

    expect(getErrorMessage(error)).toBe('오류가 발생했습니다.');
  });
});

describe('getErrorCode', () => {
  it('AxiosError에서 에러 코드를 추출한다', () => {
    const error = new AxiosError('Network Error');
    error.response = {
      data: {
        error: {
          code: 'INVALID_REQUEST',
        },
      },
    } as any;

    expect(getErrorCode(error)).toBe('INVALID_REQUEST');
  });

  it('에러 코드가 없으면 undefined를 반환한다', () => {
    const error = new AxiosError('Network Error');
    error.response = {
      data: {},
    } as any;

    expect(getErrorCode(error)).toBeUndefined();
  });

  it('AxiosError가 아닌 경우 undefined를 반환한다', () => {
    const error = new Error('일반 에러');
    expect(getErrorCode(error)).toBeUndefined();
  });

  it('response가 없는 경우 undefined를 반환한다', () => {
    const error = new AxiosError('Network Error');
    expect(getErrorCode(error)).toBeUndefined();
  });

  it('error.data가 없는 경우 undefined를 반환한다', () => {
    const error = new AxiosError('Network Error');
    error.response = {} as any;
    expect(getErrorCode(error)).toBeUndefined();
  });
});
