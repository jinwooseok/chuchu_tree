'use client';

import { useUser } from '../model/queries';
import { Loader, InlineFallback } from '@/shared/ui';

export function UserProfile() {
  const { data: user, isLoading, error } = useUser();

  if (isLoading) return <Loader size="md" text="사용자 정보 로딩 중..." />;
  if (error) return <InlineFallback error={error as Error} />;

  return (
    <div>
      <h1>{user?.username}</h1>
      <p>티어: {user?.tier}</p>
    </div>
  );
}
