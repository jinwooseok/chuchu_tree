/**
 * 태그 대시보드 유틸리티 함수 테스트
 */

import { getLevelColorClasses, getDaysAgo, calculateProgress, calculatePeekPosition, calculateBoxPosition } from './utils';

describe('getLevelColorClasses', () => {
  it('INTERMEDIATE 레벨의 색상 클래스를 반환한다', () => {
    const result = getLevelColorClasses('INTERMEDIATE');
    expect(result).toEqual({
      bg: 'bg-intermediate-bg',
      text: 'text-intermediate-text',
      border: 'border-intermediate-bg',
      borderTop: 'border-t-intermediate-bg',
      short: 'I',
    });
  });

  it('ADVANCED 레벨의 색상 클래스를 반환한다', () => {
    const result = getLevelColorClasses('ADVANCED');
    expect(result).toEqual({
      bg: 'bg-advanced-bg',
      text: 'text-advanced-text',
      border: 'border-advanced-bg',
      borderTop: 'border-t-advanced-bg',
      short: 'A',
    });
  });

  it('MASTER 레벨의 색상 클래스를 반환한다', () => {
    const result = getLevelColorClasses('MASTER');
    expect(result).toEqual({
      bg: 'bg-master-bg',
      text: 'text-master-text',
      border: 'border-master-bg',
      borderTop: 'border-t-master-bg',
      short: 'M',
    });
  });

  it('LOCKED 레벨의 색상 클래스를 반환한다', () => {
    const result = getLevelColorClasses('LOCKED');
    expect(result).toEqual({
      bg: 'bg-locked-bg',
      text: 'text-locked-text',
      border: 'border-locked-bg',
      borderTop: 'border-t-locked-bg',
      short: 'L',
    });
  });

  it('EXCLUDED 레벨의 색상 클래스를 반환한다', () => {
    const result = getLevelColorClasses('EXCLUDED');
    expect(result).toEqual({
      bg: 'bg-excluded-bg',
      text: 'text-excluded-text',
      border: 'border-excluded-bg',
      borderTop: 'border-t-excluded-bg',
      short: 'EX',
    });
  });

  it('알 수 없는 레벨은 기본값을 반환한다', () => {
    const result = getLevelColorClasses('UNKNOWN' as any);
    expect(result).toEqual({
      bg: 'bg-gray-300',
      text: 'text-gray-700',
      border: 'border-gray-300',
      borderTop: 'border-t-gray-300',
      short: 'D',
    });
  });
});

describe('getDaysAgo', () => {
  beforeEach(() => {
    // 시간 Mock 설정: 2024-01-15 00:00:00
    jest.useFakeTimers();
    jest.setSystemTime(new Date('2024-01-15T00:00:00.000Z'));
  });

  afterEach(() => {
    // Mock 해제
    jest.useRealTimers();
  });

  it('오늘 날짜는 0일을 반환한다', () => {
    const result = getDaysAgo('2024-01-15');
    expect(result).toBe(0);
  });

  it('어제 날짜는 1일을 반환한다', () => {
    const result = getDaysAgo('2024-01-14');
    expect(result).toBe(1);
  });

  it('3일 전 날짜는 3일을 반환한다', () => {
    const result = getDaysAgo('2024-01-12');
    expect(result).toBe(3);
  });

  it('일주일 전 날짜는 7일을 반환한다', () => {
    const result = getDaysAgo('2024-01-08');
    expect(result).toBe(7);
  });

  it('미래 날짜는 0을 반환한다', () => {
    const result = getDaysAgo('2024-01-20');
    expect(result).toBe(0);
  });
});

describe('calculateProgress', () => {
  it('진행률 0%를 계산한다', () => {
    const result = calculateProgress({
      solvedCnt: 0,
      requireSolveCnt: 10,
      userTier: 10,
      requireTier: 10,
      highest: 10,
      requireHighest: 10,
    });
    // solvedPoint: 0, userTierPoint: 30, highestPoint: 10
    expect(result).toBe(40);
  });

  it('진행률 50%를 계산한다', () => {
    const result = calculateProgress({
      solvedCnt: 5,
      requireSolveCnt: 10,
      userTier: 10,
      requireTier: 10,
      highest: 10,
      requireHighest: 10,
    });
    // solvedPoint: 30, userTierPoint: 30, highestPoint: 10
    expect(result).toBe(70);
  });

  it('진행률 100%를 계산한다', () => {
    const result = calculateProgress({
      solvedCnt: 10,
      requireSolveCnt: 10,
      userTier: 10,
      requireTier: 10,
      highest: 10,
      requireHighest: 10,
    });
    // solvedPoint: 60, userTierPoint: 30, highestPoint: 10
    expect(result).toBe(100);
  });

  it('최대값을 초과하는 경우 60점으로 제한한다', () => {
    const result = calculateProgress({
      solvedCnt: 20,
      requireSolveCnt: 10,
      userTier: 10,
      requireTier: 10,
      highest: 10,
      requireHighest: 10,
    });
    // solvedPoint: 60 (최대값), userTierPoint: 30, highestPoint: 10
    expect(result).toBe(100);
  });

  it('티어 차이가 3 이상이면 userTierPoint는 0이다', () => {
    const result = calculateProgress({
      solvedCnt: 0,
      requireSolveCnt: 10,
      userTier: 10,
      requireTier: 13,
      highest: 10,
      requireHighest: 10,
    });
    // userTierNum = 3, userTierPoint: 0
    expect(result).toBe(10); // solvedPoint: 0, userTierPoint: 0, highestPoint: 10
  });

  it('티어 차이가 2이면 userTierPoint는 10이다', () => {
    const result = calculateProgress({
      solvedCnt: 0,
      requireSolveCnt: 10,
      userTier: 10,
      requireTier: 12,
      highest: 10,
      requireHighest: 10,
    });
    // userTierNum = 2, userTierPoint: 10
    expect(result).toBe(20); // solvedPoint: 0, userTierPoint: 10, highestPoint: 10
  });

  it('티어 차이가 1이면 userTierPoint는 20이다', () => {
    const result = calculateProgress({
      solvedCnt: 0,
      requireSolveCnt: 10,
      userTier: 10,
      requireTier: 11,
      highest: 10,
      requireHighest: 10,
    });
    // userTierNum = 1, userTierPoint: 20
    expect(result).toBe(30); // solvedPoint: 0, userTierPoint: 20, highestPoint: 10
  });

  it('티어 차이가 0이면 userTierPoint는 30이다', () => {
    const result = calculateProgress({
      solvedCnt: 0,
      requireSolveCnt: 10,
      userTier: 10,
      requireTier: 10,
      highest: 10,
      requireHighest: 10,
    });
    // userTierNum = 0, userTierPoint: 30
    expect(result).toBe(40); // solvedPoint: 0, userTierPoint: 30, highestPoint: 10
  });

  it('highest가 requireHighest보다 작으면 highestPoint는 0이다', () => {
    const result = calculateProgress({
      solvedCnt: 0,
      requireSolveCnt: 10,
      userTier: 10,
      requireTier: 10,
      highest: 5,
      requireHighest: 10,
    });
    // highestPoint: 0
    expect(result).toBe(30); // solvedPoint: 0, userTierPoint: 30, highestPoint: 0
  });

  it('highest가 requireHighest 이상이면 highestPoint는 10이다', () => {
    const result = calculateProgress({
      solvedCnt: 0,
      requireSolveCnt: 10,
      userTier: 10,
      requireTier: 10,
      highest: 15,
      requireHighest: 10,
    });
    // highestPoint: 10
    expect(result).toBe(40); // solvedPoint: 0, userTierPoint: 30, highestPoint: 10
  });
});

describe('calculatePeekPosition', () => {
  it('0% 비율일 때 위치를 계산한다', () => {
    const result = calculatePeekPosition(0);
    expect(result).toBe(10); // (0 * 80 / 100) + 10
  });

  it('50% 비율일 때 위치를 계산한다', () => {
    const result = calculatePeekPosition(50);
    expect(result).toBe(50); // (50 * 80 / 100) + 10
  });

  it('100% 비율일 때 위치를 계산한다', () => {
    const result = calculatePeekPosition(100);
    expect(result).toBe(90); // (100 * 80 / 100) + 10
  });

  it('75% 비율일 때 위치를 계산한다', () => {
    const result = calculatePeekPosition(75);
    expect(result).toBe(70); // (75 * 80 / 100) + 10
  });
});

describe('calculateBoxPosition', () => {
  it('0% 비율일 때 박스 위치를 계산한다', () => {
    const result = calculateBoxPosition(0, 'INTERMEDIATE');
    const nameLength = 'INTERMEDIATE'.length;
    const expected = Math.round((0 * 80) / 100) + 10 + ((50 - 0) / 100) * nameLength * 2.3;
    expect(result).toBe(expected);
  });

  it('50% 비율일 때 박스 위치를 계산한다', () => {
    const result = calculateBoxPosition(50, 'ADVANCED');
    const nameLength = 'ADVANCED'.length;
    const expected = Math.round((50 * 80) / 100) + 10 + ((50 - 50) / 100) * nameLength * 2.3;
    expect(result).toBe(50); // 50 + 0
  });

  it('100% 비율일 때 박스 위치를 계산한다', () => {
    const result = calculateBoxPosition(100, 'MASTER');
    const nameLength = 'MASTER'.length;
    const expected = Math.round((100 * 80) / 100) + 10 + ((50 - 100) / 100) * nameLength * 2.3;
    expect(result).toBe(expected);
  });

  it('짧은 이름일 때 박스 위치를 계산한다', () => {
    const result = calculateBoxPosition(25, 'LOCKED');
    const nameLength = 'LOCKED'.length;
    const expected = Math.round((25 * 80) / 100) + 10 + ((50 - 25) / 100) * nameLength * 2.3;
    expect(result).toBe(expected);
  });

  it('긴 이름일 때 박스 위치를 계산한다', () => {
    const result = calculateBoxPosition(75, 'EXCLUDED');
    const nameLength = 'EXCLUDED'.length;
    const expected = Math.round((75 * 80) / 100) + 10 + ((50 - 75) / 100) * nameLength * 2.3;
    expect(result).toBe(expected);
  });
});
