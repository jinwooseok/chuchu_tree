'use client';

import { Calendar, dateFnsLocalizer, ToolbarProps, EventProps } from 'react-big-calendar';
import { format, parse, startOfWeek, getDay, isSameDay } from 'date-fns';
import { ko } from 'date-fns/locale';
import 'react-big-calendar/lib/css/react-big-calendar.css';
import { ComponentType, useMemo } from 'react';

import { transformToCalendarEvents, getDisplayTags } from '../lib/utils';
import { CalendarEvent } from '@/shared/types/calendar';
import { TAG_INFO } from '@/shared/constants/tagSystem';
import { useCalendarStore } from '@/lib/store/calendar';

const locales = {
  ko: ko,
};

const localizer = dateFnsLocalizer({
  format,
  parse,
  startOfWeek,
  getDay,
  locales,
});

// 커스텀 툴바
function CustomToolbar({ date, onNavigate }: ToolbarProps) {
  return (
    <div className="mb-4 flex items-center justify-between">
      {/* 좌측: 년/월 표시 */}
      <div className="text-lg font-semibold">{format(date, 'yyyy M월', { locale: ko })}</div>

      {/* 우측: 네비게이션 버튼 */}
      <div className="flex gap-2">
        <button onClick={() => onNavigate('TODAY')} className="rounded bg-gray-200 px-3 py-1 text-xs hover:bg-gray-300">
          오늘
        </button>
        <button onClick={() => onNavigate('PREV')} className="rounded bg-gray-200 px-3 py-1 text-xs hover:bg-gray-300">
          이전
        </button>
        <button onClick={() => onNavigate('NEXT')} className="rounded bg-gray-200 px-3 py-1 text-xs hover:bg-gray-300">
          다음
        </button>
      </div>
    </div>
  );
}

// 커스텀 MonthEvent 컴포넌트 (각 날짜 셀 내부에 표시되는 이벤트)
function CustomMonthEvent({ event }: EventProps<CalendarEvent>) {
  // 이 컴포넌트는 개별 이벤트를 렌더링하지 않음 (빈 div 반환)
  // 대신 MonthDateHeader에서 모든 이벤트를 그룹핑해서 표시
  return null;
}

// 커스텀 MonthDateHeader 컴포넌트 (각 날짜 셀의 날짜 숫자 부분)
interface CustomMonthDateHeaderProps {
  date: Date;
  label: string;
  allEvents: CalendarEvent[];
}

function CustomMonthDateHeader({ date, label, allEvents }: CustomMonthDateHeaderProps) {
  // 현재 날짜에 해당하는 이벤트들만 필터링
  const dayEvents = allEvents.filter((event) => isSameDay(new Date(event.start), date));

  const { displayTags, hasMore, moreCount } = getDisplayTags(dayEvents);

  return (
    <div className="flex h-full flex-col">
      {/* 날짜 숫자 */}
      <div className="text-right text-sm">{label}</div>

      {/* 태그 목록 */}
      {displayTags.length > 0 && (
        <div className="mt-1 flex flex-col gap-1">
          {displayTags.map((event, index) => {
            const tagCode = event.resource.tagCode;
            const tagInfo = TAG_INFO[tagCode as keyof typeof TAG_INFO];
            const isSolved = event.resource.type === 'solved';

            // will solve는 회색, solved는 tag별 색상
            const bgColorClass = isSolved && tagInfo ? tagInfo.bgColor : 'bg-gray-300';

            return (
              <div key={`${event.resource.problem.problemId}-${tagCode}-${index}`} className={`rounded px-2 py-0.5 text-xs ${bgColorClass}`}>
                {event.title}
              </div>
            );
          })}
          {hasMore && <div className="rounded bg-gray-100 px-2 py-0.5 text-xs text-gray-600">+{moreCount}개 더보기</div>}
        </div>
      )}
    </div>
  );
}

export default function BigCalendar() {
  // Zustand 스토어에서 데이터 가져오기
  const monthlyData = useCalendarStore((state) => state.monthlyData);
  const setSelectedDate = useCalendarStore((state) => state.setSelectedDate);

  // mock 데이터를 react-big-calendar 이벤트로 변환
  const events = useMemo(() => {
    return transformToCalendarEvents(monthlyData);
  }, [monthlyData]);

  // MonthDateHeader를 래핑하여 allEvents를 전달
  const CustomMonthDateHeaderWrapper = useMemo(() => {
    // eslint-disable-next-line react/display-name
    return ({ date, label }: { date: Date; label: string }) => <CustomMonthDateHeader date={date} label={label} allEvents={events} />;
  }, [events]);

  // 날짜 클릭 핸들러
  const handleSelectSlot = ({ start }: { start: Date }) => {
    setSelectedDate(start);
  };

  return (
    <div className="calendar-12px h-full w-full">
      <style jsx global>{`
        .rbc-event,
        .rbc-event-label,
        .rbc-event-content {
          display: none !important;
        }
      `}</style>
      <Calendar
        localizer={localizer}
        events={events}
        startAccessor="start"
        endAccessor="end"
        style={{ height: '100%' }}
        culture="ko"
        views={['month']}
        defaultView="month"
        selectable
        onSelectSlot={handleSelectSlot}
        components={{
          toolbar: CustomToolbar as ComponentType<ToolbarProps>,
          month: {
            dateHeader: CustomMonthDateHeaderWrapper as ComponentType<any>,
          },
        }}
      />
    </div>
  );
}
