import { useLandingCalendar } from '@/features/landing';
import dynamic from 'next/dynamic';
import { useCalendarStore } from '@/lib/store/calendar';
import { useState, useEffect } from 'react';
import { isSameMonth } from 'date-fns';
import { CalendarSidebarInset } from '@/features/calendar';

// 클라이언트 전용 렌더링 (hydration mismatch 방지)
const SmallCalendar = dynamic(() => import('@/features/calendar').then((mod) => mod.SmallCalendar), {
  ssr: false,
  loading: () => (
    <div className="flex items-center justify-center" style={{ minHeight: '300px' }}>
      <div className="text-sm text-gray-400">Loading...</div>
    </div>
  ),
});

export default function LandingCalendarSidebar() {
  const { selectedDate, bigCalendarDate } = useCalendarStore();

  // SmallCalendar의 현재 표시 월 관리
  const [activeStartDate, setActiveStartDate] = useState<Date>(bigCalendarDate || selectedDate || new Date());

  // BigCalendar의 월이 변경되면 SmallCalendar도 따라감
  useEffect(() => {
    if (bigCalendarDate && !isSameMonth(bigCalendarDate, activeStartDate)) {
      setActiveStartDate(bigCalendarDate);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [bigCalendarDate]); // activeStartDate 제거 (무한 루프 방지)

  // activeStartDate 기준으로 데이터 fetch
  const year = activeStartDate.getFullYear();
  const month = activeStartDate.getMonth() + 1;
  const calendarData = useLandingCalendar({ year: year, month: month });

  return (
    <div className="hide-scrollbar flex h-full flex-col gap-8 overflow-y-auto p-4">
      <div>
        <div className="text-white cursor-default select-none bg-primary w-full px-2 py-2 rounded-sm text-sm font-medium mb-2">ChuchuTree 튜토리얼</div>
        <SmallCalendar calendarData={calendarData} activeStartDate={activeStartDate} onActiveStartDateChange={setActiveStartDate} />
      </div>
      <CalendarSidebarInset calendarData={calendarData} isLanding={true} />
    </div>
  );
}
