interface LoaderProps {
  size?: 'sm' | 'md' | 'lg';
  text?: string;
  fullScreen?: boolean;
}

export function Loader({ size = 'md', text, fullScreen = false }: LoaderProps) {
  const sizeClasses = {
    sm: 'h-4 w-4 border-2',
    md: 'h-8 w-8 border-3',
    lg: 'h-12 w-12 border-4',
  };

  const containerClasses = fullScreen
    ? 'flex min-h-screen w-full flex-col items-center justify-center gap-4'
    : 'flex w-full flex-col items-center justify-center gap-4 p-8';

  return (
    <div className={containerClasses}>
      <div
        className={`${sizeClasses[size]} animate-spin rounded-full border-primary border-t-transparent`}
        role="status"
        aria-label="로딩 중"
      />
      {text && <p className="text-sm text-muted-foreground">{text}</p>}
    </div>
  );
}

// 전체 페이지 로딩용
export function PageLoader({ text }: { text?: string }) {
  return <Loader size="lg" text={text || '페이지를 불러오는 중...'} fullScreen />;
}

// 스켈레톤 로더 (카드형)
export function SkeletonCard() {
  return (
    <div className="w-full animate-pulse space-y-4 rounded-lg border bg-card p-6">
      <div className="h-4 w-3/4 rounded bg-muted" />
      <div className="space-y-2">
        <div className="h-3 w-full rounded bg-muted" />
        <div className="h-3 w-5/6 rounded bg-muted" />
      </div>
    </div>
  );
}

// 스켈레톤 로더 (리스트형)
export function SkeletonList({ count = 3 }: { count?: number }) {
  return (
    <div className="w-full space-y-3">
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="flex animate-pulse items-center gap-4 rounded-lg border bg-card p-4">
          <div className="h-12 w-12 rounded-full bg-muted" />
          <div className="flex-1 space-y-2">
            <div className="h-4 w-1/2 rounded bg-muted" />
            <div className="h-3 w-3/4 rounded bg-muted" />
          </div>
        </div>
      ))}
    </div>
  );
}

// 인라인 스피너 (버튼 내부 등에 사용)
export function Spinner({ size = 'sm' }: { size?: 'sm' | 'md' | 'lg' }) {
  const sizeClasses = {
    sm: 'h-4 w-4 border-2',
    md: 'h-6 w-6 border-2',
    lg: 'h-8 w-8 border-3',
  };

  return (
    <div
      className={`${sizeClasses[size]} inline-block animate-spin rounded-full border-current border-t-transparent`}
      role="status"
      aria-label="로딩 중"
    />
  );
}
