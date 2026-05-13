/**
 * Jest + RTL 환경 테스트용 샘플 테스트
 * 테스트 인프라가 제대로 구축되었는지 확인
 */

describe('Jest 환경 테스트', () => {
  it('기본 테스트가 실행된다', () => {
    expect(true).toBe(true);
  });

  it('숫자 계산이 정확하다', () => {
    expect(1 + 1).toBe(2);
  });

  it('문자열 비교가 동작한다', () => {
    expect('hello').toBe('hello');
  });
});

describe('TypeScript 타입 체크', () => {
  it('타입이 올바르게 추론된다', () => {
    const num: number = 42;
    const str: string = 'test';

    expect(typeof num).toBe('number');
    expect(typeof str).toBe('string');
  });
});
