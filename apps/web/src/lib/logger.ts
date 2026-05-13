const isDev = process.env.NODE_ENV === 'development';

/** 서버 콘솔에 출력 (환경 무관) */
export const serverLog = (...args: unknown[]): void => {
  console.log(...args);
};

/** 브라우저 콘솔에 출력 (개발 환경에서만) */
export const clientLog = (...args: unknown[]): void => {
  if (isDev) {
    console.log(...args);
  }
};
