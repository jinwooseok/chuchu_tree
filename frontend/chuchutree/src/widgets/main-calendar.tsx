'use client';

import { RefreshButtonContainer } from '@/features/refresh';
import dynamic from 'next/dynamic';

// 클라이언트 전용 렌더링 (hydration mismatch 방지)
const BigCalendar = dynamic(() => import('@/features/calendar/ui/BigCalendar'), {
  ssr: false,
  loading: () => (
    <div className="flex h-full w-full items-center justify-center">
      <div className="text-sm text-gray-400">Loading...</div>
    </div>
  ),
});

export default function MainCalendar() {
  return (
    <div className="bg-innerground-white relative h-full w-full p-4">
      <BigCalendar />
      <RefreshButtonContainer />
    </div>
  );
}
