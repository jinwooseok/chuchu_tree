import { useCalendar } from '@/entities/calendar';
import { CalendarSidebarInset } from '@/features/calendar-sidebar';
import dynamic from 'next/dynamic';
import { useCalendarStore } from '@/lib/store/calendar';
import { useState, useEffect } from 'react';
import { isSameMonth } from 'date-fns';

// 클라이언트 전용 렌더링 (hydration mismatch 방지)
const SmallCalendar = dynamic(() => import('@/features/calendar/ui/SmallCalendar'), {
  ssr: false,
  loading: () => (
    <div className="flex items-center justify-center" style={{ minHeight: '300px' }}>
      <div className="text-sm text-gray-400">Loading...</div>
    </div>
  ),
});

export default function CalendarSidebar() {
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
  const { data: calendarData } = useCalendar(year, month);

  return (
    <div className="hide-scrollbar flex h-full flex-col gap-8 overflow-y-auto p-4">
      <SmallCalendar calendarData={calendarData} activeStartDate={activeStartDate} onActiveStartDateChange={setActiveStartDate} />
      <CalendarSidebarInset calendarData={calendarData} isLanding={true} />
    </div>
  );
}
