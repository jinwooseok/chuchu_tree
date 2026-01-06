'use client';

import { Calendar, dateFnsLocalizer, ToolbarProps, EventProps } from 'react-big-calendar';
import { format, parse, startOfWeek, getDay, isSameDay, isToday } from 'date-fns';
import { ko } from 'date-fns/locale';
import 'react-big-calendar/lib/css/react-big-calendar.css';
import { ComponentType, useMemo, useState, useEffect } from 'react';

import { transformToCalendarEvents, getDisplayTags } from '../lib/utils';
import { CalendarEvent, useCalendar } from '@/entities/calendar';
import { TAG_INFO } from '@/shared/constants/tagSystem';
import { useCalendarStore } from '@/lib/store/calendar';
import { ChevronDown, ChevronUp } from 'lucide-react';

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

// 커스텀 툴바 (외부에서 onNavigate를 받음)
interface CustomToolbarPropsWithHandler extends ToolbarProps {
  onNavigateCustom: (action: 'PREV' | 'NEXT' | 'TODAY') => void;
}

function CustomToolbar({ date, onNavigate, onNavigateCustom }: CustomToolbarPropsWithHandler) {
  const handleClick = (action: 'PREV' | 'NEXT' | 'TODAY') => {
    onNavigate(action); // react-big-calendar의 내부 상태 업데이트
    onNavigateCustom(action); // 우리의 커스텀 핸들러 (API 요청)
  };

  return (
    <div className="mb-4 flex items-center justify-between">
      {/* 좌측: 년/월 표시 */}
      <div className="text-lg font-semibold" suppressHydrationWarning>
        {format(date, 'yyyy M월', { locale: ko })}
      </div>

      {/* 우측: 네비게이션 버튼 */}
      <div className="flex gap-2">
        <button onClick={() => handleClick('TODAY')} className="hover:bg-background rounded border px-3 py-1 text-xs" title="오늘로 이동">
          오늘
        </button>
        <button onClick={() => handleClick('PREV')} className="hover:bg-background rounded px-3 py-1 text-xs" title="지난달로 이동">
          <ChevronUp className="h-4 w-4" />
        </button>
        <button onClick={() => handleClick('NEXT')} className="hover:bg-background rounded px-3 py-1 text-xs" title="다음 달로 이동">
          <ChevronDown className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
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

  const today = isToday(date);

  return (
    <div className="flex h-full flex-col">
      {/* 날짜 숫자 */}
      <div className="mt-1 text-right text-sm" suppressHydrationWarning>
        {today ? <span className="bg-primary inline-flex h-6 w-6 items-center justify-center rounded text-white">{label}</span> : label}
      </div>

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
              <div key={`${event.resource.problem.problemId}-${tagCode}-${index}`} className={`rounded px-2 py-0.5 text-xs ${bgColorClass} text-gray-800`}>
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
  const { monthlyData, actions } = useCalendarStore();
  const { setSelectedDate, setCalendarData } = actions;

  // 현재 표시 중인 월 관리 (초기값: 오늘 날짜)
  const [currentDate, setCurrentDate] = useState(new Date());
  const year = currentDate.getFullYear();
  const month = currentDate.getMonth() + 1;

  // 해당 월의 calendar 데이터 fetch
  const { data: calendarData, isLoading } = useCalendar(year, month);

  // 데이터가 로드되면 store에 저장
  useEffect(() => {
    if (calendarData) {
      setCalendarData(calendarData);
    }
  }, [calendarData, setCalendarData]);

  // calendar 데이터를 react-big-calendar 이벤트로 변환
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

  // 월 네비게이션 핸들러
  const handleNavigate = (action: 'PREV' | 'NEXT' | 'TODAY') => {
    const newDate = new Date(currentDate);

    if (action === 'PREV') {
      newDate.setMonth(newDate.getMonth() - 1);
    } else if (action === 'NEXT') {
      newDate.setMonth(newDate.getMonth() + 1);
    } else if (action === 'TODAY') {
      setCurrentDate(new Date());
      return;
    }

    setCurrentDate(newDate);
  };

  return (
    <div className="calendar-12px h-full w-full">
      <style jsx global>{`
        .rbc-event,
        .rbc-event-label,
        .rbc-event-content {
          display: none !important;
        }

        /* 날짜 칸 클릭 시 애니메이션 */
        .rbc-day-bg:active {
          background-color: rgba(0, 0, 0, 0.05);
          transition: background-color 0.1s ease;
        }
        .rbc-off-range-bg {
          background-color: transparent;
        }
        /* 캘린더 그리드 border 설정 */

        .rbc-header {
          border-left: transparent !important;
        }
        .rbc-month-view {
          border: transparent !important;
        }
        .rbc-today {
          background-color: transparent !important;
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
        date={currentDate}
        onNavigate={(newDate) => setCurrentDate(newDate)}
        selectable
        onSelectSlot={handleSelectSlot}
        components={{
          toolbar: ((props: ToolbarProps) => <CustomToolbar {...props} onNavigateCustom={handleNavigate} />) as ComponentType<ToolbarProps>,
          month: {
            dateHeader: CustomMonthDateHeaderWrapper as ComponentType<any>,
          },
        }}
      />
    </div>
  );
}
