'use client';

import { UserProfile } from '@/entities/user';
import { useCount, usePlusCount, useMinusCount } from '@/lib/store/zustand_test_count';
import ThemeButton from '@/shared/ui/theme-button';

export default function TestPage() {
  const { num } = useCount();
  const plus = usePlusCount();
  const minus = useMinusCount();
  return (
    <>
      <div>{num}</div>
      <div onClick={() => plus(2)}>+2</div>
      <div onClick={minus}>-</div>

      <ThemeButton />
      <UserProfile />
    </>
  );
}
