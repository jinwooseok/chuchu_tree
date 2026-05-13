import type { Config } from 'jest';
import nextJest from 'next/jest';

const createJestConfig = nextJest({
  // Next.js 앱의 경로를 제공하여 next.config.ts 및 .env 파일을 로드
  dir: './',
});

// Jest에 전달할 사용자 정의 설정
const config: Config = {
  // 각 테스트 실행 전에 더 많은 설정 옵션을 추가
  setupFilesAfterEnv: ['<rootDir>/jest.setup.ts'],

  // jsdom을 사용하여 브라우저와 유사한 환경에서 테스트 실행
  testEnvironment: 'jsdom',

  // 경로 매핑 (tsconfig.json의 paths와 동일하게 설정)
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1',
  },

  // 커버리지 수집 대상 파일
  collectCoverageFrom: [
    'src/**/*.{js,jsx,ts,tsx}',
    '!src/**/*.d.ts',
    '!src/**/*.stories.{js,jsx,ts,tsx}',

    // App Router 라우팅 파일만 제외 (클라이언트 컴포넌트는 포함)
    '!src/app/**/page.tsx',
    '!src/app/**/layout.tsx',
    '!src/app/**/loading.tsx',
    '!src/app/**/error.tsx',
    '!src/app/**/not-found.tsx',
    '!src/app/**/template.tsx',
    '!src/app/**/default.tsx',
    '!src/app/robots.ts',
    '!src/app/sitemap.ts',

    '!src/components/ui/**', // shadcn/ui 컴포넌트 제외
    '!src/**/*.test.{ts,tsx}', // 테스트 파일 제외
    '!src/**/*.spec.{ts,tsx}', // 스펙 파일 제외
    '!src/lib/test-utils/**', // 테스트 유틸리티 제외
  ],

  // 커버리지 임계값 설정
  coverageThreshold: {
    global: {
      statements: 45,
      branches: 40,
      functions: 45,
      lines: 45,
    },
  },

  // 테스트 파일 패턴
  testMatch: [
    '**/__tests__/**/*.[jt]s?(x)',
    '**/?(*.)+(spec|test).[jt]s?(x)',
  ],
};

// createJestConfig는 비동기이므로 Next.js가 설정을 로드할 수 있도록 export
export default createJestConfig(config);
