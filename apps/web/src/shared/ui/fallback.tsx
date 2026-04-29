'use client';

interface FallbackProps {
  error?: Error;
  reset?: () => void;
  title?: string;
  description?: string;
}

export function Fallback({ error, reset, title, description }: FallbackProps) {
  return (
    <div className="flex min-h-[400px] w-full flex-col items-center justify-center gap-4 p-8">
      <div className="flex flex-col items-center gap-2 text-center">
        <h2 className="text-2xl font-semibold text-destructive">
          {title || '오류가 발생했습니다'}
        </h2>
        <p className="text-muted-foreground">
          {description || error?.message || '문제가 발생했습니다. 잠시 후 다시 시도해주세요.'}
        </p>
      </div>

      {reset && (
        <button
          onClick={reset}
          className="rounded-md bg-primary px-4 py-2 text-primary-foreground transition-colors hover:bg-primary/90"
        >
          다시 시도
        </button>
      )}
    </div>
  );
}

// 전체 페이지 에러용
export function PageFallback({ error, reset }: FallbackProps) {
  return (
    <div className="flex min-h-screen w-full flex-col items-center justify-center gap-4 p-8">
      <div className="flex flex-col items-center gap-2 text-center">
        <h1 className="text-4xl font-bold text-destructive">에러 발생</h1>
        <p className="text-lg text-muted-foreground">{error?.message || '알 수 없는 오류가 발생했습니다.'}</p>
      </div>

      {reset && (
        <button
          onClick={reset}
          className="rounded-md bg-primary px-6 py-3 text-lg text-primary-foreground transition-colors hover:bg-primary/90"
        >
          새로고침
        </button>
      )}
    </div>
  );
}

// 작은 컴포넌트 에러용
export function InlineFallback({ error, reset }: FallbackProps) {
  return (
    <div className="flex w-full flex-col items-center gap-2 rounded-md border border-destructive/50 bg-destructive/10 p-4">
      <p className="text-sm text-destructive">{error?.message || '데이터를 불러올 수 없습니다.'}</p>
      {reset && (
        <button onClick={reset} className="text-xs text-primary underline hover:no-underline">
          다시 시도
        </button>
      )}
    </div>
  );
}
