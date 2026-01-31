/**
 * 날짜 포맷팅 유틸리티 함수 테스트
 */

import { formatDateString } from './date';

describe('formatDateString', () => {
  it('Date 객체를 YYYY-MM-DD 형식으로 변환한다', () => {
    const date = new Date('2024-01-05');
    expect(formatDateString(date)).toBe('2024-01-05');
  });

  it('한 자리 월과 일을 0으로 패딩한다', () => {
    const date = new Date('2024-01-05');
    expect(formatDateString(date)).toBe('2024-01-05');
  });

  it('12월 31일을 올바르게 변환한다', () => {
    const date = new Date('2024-12-31');
    expect(formatDateString(date)).toBe('2024-12-31');
  });

  it('윤년 2월 29일을 올바르게 변환한다', () => {
    const date = new Date('2024-02-29');
    expect(formatDateString(date)).toBe('2024-02-29');
  });

  it('1월 1일을 올바르게 변환한다', () => {
    const date = new Date('2024-01-01');
    expect(formatDateString(date)).toBe('2024-01-01');
  });

  it('두 자리 월과 일을 올바르게 변환한다', () => {
    const date = new Date('2024-11-25');
    expect(formatDateString(date)).toBe('2024-11-25');
  });
});
