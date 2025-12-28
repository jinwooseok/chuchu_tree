'use client';

import { useUser } from '../model/queries';

export function UserProfile() {
  const { data: user, isLoading } = useUser();

  if (isLoading) return <div>로딩중...</div>;

  return (
    <div>
      <h1>{user?.username}</h1>
      <p>티어: {user?.tier}</p>
    </div>
  );
}
