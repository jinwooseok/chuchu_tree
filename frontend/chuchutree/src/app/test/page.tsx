'use client';

import { useCount, usePlusCount, useMinusCount } from '@/lib/store/zustand_test_count';

export default function TestPage() {
  const { num } = useCount();
  const plus = usePlusCount();
  const minus = useMinusCount();
  return (
    <>
      <div>{num}</div>
      <div onClick={() => plus(2)}>+2</div>
      <div onClick={minus}>-</div>
    </>
  );
}
