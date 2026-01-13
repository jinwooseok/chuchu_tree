'use client';

import { Calendar, dateFnsLocalizer, ToolbarProps, EventProps } from 'react-big-calendar';
import { format, parse, startOfWeek, getDay, isSameDay, isToday, isSameMonth } from 'date-fns';
import { ko } from 'date-fns/locale';
import 'react-big-calendar/lib/css/react-big-calendar.css';
import { ComponentType, useMemo, useState, useEffect } from 'react';

import { transformToCalendarEvents, getDisplayTags } from '../lib/utils';
import { CalendarEvent, useCalendar } from '@/entities/calendar';
import { TAG_INFO } from '@/shared/constants/tagSystem';
import { useCalendarStore } from '@/lib/store/calendar';
import { ChevronDown, ChevronUp } from 'lucide-react';
import { AppTooltip } from '@/components/custom/tooltip/AppTooltip';

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

// 커스텀 툴바 - 순수 presentational component
function CustomToolbar({ date, onNavigate }: ToolbarProps) {
  const handleClick = (action: 'PREV' | 'NEXT' | 'TODAY') => {
    onNavigate(action); // react-big-calendar의 onNavigate만 호출
  };

  return (
    <div className="mb-4 flex items-center justify-between">
      {/* 좌측: 년/월 표시 */}
      <div className="text-lg font-semibold" suppressHydrationWarning>
        {format(date, 'yyyy M월', { locale: ko })}
      </div>

      {/* 우측: 네비게이션 버튼 */}
      <div className="flex gap-2">
        <AppTooltip content="오늘로 이동" side="bottom">
          <button onClick={() => handleClick('TODAY')} className="hover:bg-background rounded border px-3 py-1 text-xs" aria-label="오늘로 이동">
            오늘
          </button>
        </AppTooltip>
        <AppTooltip content="지난달로 이동" side="bottom">
          <button onClick={() => handleClick('PREV')} className="hover:bg-background rounded px-3 py-1 text-xs" aria-label="지난달로 이동">
            <ChevronUp className="h-4 w-4" />
          </button>
        </AppTooltip>
        <AppTooltip content="다음 달로 이동" side="bottom">
          <button onClick={() => handleClick('NEXT')} className="hover:bg-background rounded px-3 py-1 text-xs" aria-label="다음 달로 이동">
            <ChevronDown className="h-4 w-4" />
          </button>
        </AppTooltip>
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
  // Zustand에서 UI 상태만 가져오기
  const { selectedDate, bigCalendarDate, actions } = useCalendarStore();
  const { setSelectedDate, setBigCalendarDate } = actions;

  // 안정적인 초기 날짜 (한 번만 생성)
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
  const year = currentDate.getFullYear();
  const month = currentDate.getMonth() + 1;

  // 해당 월의 calendar 데이터 fetch (TanStack Query가 자동으로 캐시 관리)
  const { data: calendarData, isLoading } = useCalendar(year, month);

  // selectedDate가 변경되면 BigCalendar도 해당 월로 이동
  useEffect(() => {
    if (selectedDate && bigCalendarDate) {
      // 이미 같은 월이면 업데이트하지 않음
      if (!isSameMonth(selectedDate, bigCalendarDate)) {
        setBigCalendarDate(selectedDate);
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedDate]); // selectedDate 변경 시에만 실행!

  // calendar 데이터를 react-big-calendar 이벤트로 변환
  const events = useMemo(() => {
    if (!calendarData) return [];
    return transformToCalendarEvents(calendarData.monthlyData);
  }, [calendarData]);

  // MonthDateHeader를 래핑하여 allEvents를 전달
  const CustomMonthDateHeaderWrapper = useMemo(() => {
    // eslint-disable-next-line react/display-name
    return ({ date, label }: { date: Date; label: string }) => <CustomMonthDateHeader date={date} label={label} allEvents={events} />;
  }, [events]);

  // 날짜 클릭 핸들러
  const handleSelectSlot = ({ start }: { start: Date }) => {
    setSelectedDate(start);
  };

  // 네비게이션 핸들러 - single source of truth
  const handleBigCalendarNavigate = (newDate: Date) => {
    setBigCalendarDate(newDate);
  };

  return (
    <div className="calendar-12px h-full w-full">
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
        onNavigate={handleBigCalendarNavigate}
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
