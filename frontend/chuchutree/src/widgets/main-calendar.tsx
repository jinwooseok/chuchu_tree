'use client';

import { useCalendar } from '@/entities/calendar';
import { RefreshButtonContainer } from '@/features/refresh';
import { useCalendarStore } from '@/lib/store/calendar';
import dynamic from 'next/dynamic';
import { useEffect, useState } from 'react';

// 클라이언트 전용 렌더링 (hydration mismatch 방지)
const BigCalendar = dynamic(() => import('@/features/calendar').then((mod) => mod.BigCalendar), {
  ssr: false,
  loading: () => (
    <div className="flex h-full w-full items-center justify-center">
      <div className="text-sm text-gray-400">Loading...</div>
    </div>
  ),
});

export default function MainCalendar() {
  const { bigCalendarDate, actions } = useCalendarStore();
  const { setBigCalendarDate } = actions;
  const [initialDate] = useState(new Date());

  // 컴포넌트 마운트 시 bigCalendarDate가 null이면 초기 날짜로 설정 (한 번만 실행)
  useEffect(() => {
    if (!bigCalendarDate) {
      setBigCalendarDate(initialDate);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // 마운트 시 한 번만 실행

  // 현재 표시 중인 월 (store에서 관리, fallback은 initialDate)
  const currentDate = bigCalendarDate || initialDate;
  const year = currentDate?.getFullYear() || new Date().getFullYear();
  const month = (currentDate?.getMonth() || new Date().getMonth()) + 1;
  const { data: calendarData } = useCalendar(year, month);
  return (
    <div className="bg-innerground-white relative h-full w-full p-4">
      <BigCalendar calendarData={calendarData} />
      <RefreshButtonContainer />
    </div>
  );
}
