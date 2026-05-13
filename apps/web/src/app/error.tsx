'use client';

import { PageFallback } from '@/shared/ui';

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return <PageFallback error={error} reset={reset} />;
}
