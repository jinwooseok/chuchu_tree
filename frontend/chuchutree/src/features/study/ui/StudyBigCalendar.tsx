'use client';

import { Calendar, dateFnsLocalizer, ToolbarProps } from 'react-big-calendar';
import { format, parse, startOfWeek, getDay, isSameDay, isToday, isSameMonth, addMonths, subMonths } from 'date-fns';
import { ko } from 'date-fns/locale';
import 'react-big-calendar/lib/css/react-big-calendar.css';
import { ComponentType, useMemo, useState, useEffect, useRef } from 'react';

import { transformToStudyCalendarEvents } from '../lib/utils';
import { CalendarEvent } from '@/entities/calendar';
import { StudyCalendar } from '@/entities/study';
import { TAG_INFO, TagKey } from '@/shared/constants/tagSystem';
import { useStudyCalendarStore } from '@/lib/store/studyCalendar';
import { ChevronDown, ChevronUp } from 'lucide-react';
import { AppTooltip } from '@/components/custom/tooltip/AppTooltip';
import { useSidebar } from '@/components/ui/sidebar';
import { useGlobalShortcuts } from '@/lib/hooks/useGlobalShortcuts';
import { useLayoutStore } from '@/lib/store/layout';

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
  const handleClick = (action: 'PREV' | 'NEXT' | 'TODAY') => {
    onNavigate(action);
  };

  return (
    <div className="mb-4 flex items-center justify-between">
      <div className="cursor-default text-lg font-semibold" suppressHydrationWarning>
        {format(date, 'yyyy M월', { locale: ko })}
      </div>
      <div className="flex gap-2">
        <AppTooltip content="오늘로 이동" side="bottom" shortCut1="Alt" shortCut2="T">
          <button onClick={() => handleClick('TODAY')} className="hover:bg-background cursor-pointer rounded border px-3 py-1 text-xs" aria-label="오늘로 이동">
            오늘
          </button>
        </AppTooltip>
        <AppTooltip content="지난달로 이동" side="bottom" shortCut1="Alt" shortCut2="↑">
          <button onClick={() => handleClick('PREV')} className="hover:bg-background cursor-pointer rounded px-3 py-1 text-xs" aria-label="지난달로 이동">
            <ChevronUp className="h-4 w-4" />
          </button>
        </AppTooltip>
        <AppTooltip content="다음 달로 이동" side="bottom" shortCut1="Alt" shortCut2="↓">
          <button onClick={() => handleClick('NEXT')} className="hover:bg-background cursor-pointer rounded px-3 py-1 text-xs" aria-label="다음 달로 이동">
            <ChevronDown className="h-4 w-4" />
          </button>
        </AppTooltip>
      </div>
    </div>
  );
}

// 커스텀 MonthDateHeader
interface CustomMonthDateHeaderProps {
  date: Date;
  label: string;
  allEvents: CalendarEvent[];
}

function CustomMonthDateHeader({ date, label, allEvents }: CustomMonthDateHeaderProps) {
  const dayEvents = allEvents.filter((event) => isSameDay(new Date(event.start), date));

  // 기존 getDisplayTags 로직 인라인 (최대 3개, 4개 이상이면 2개 + "+n더보기")
  const solvedEvents = dayEvents.filter((e) => e.resource.type === 'solved');
  const willSolveEvents = dayEvents.filter((e) => e.resource.type === 'willSolve');
  const allTags = [...solvedEvents, ...willSolveEvents];
  const totalCount = allTags.length;
  const MAX_DISPLAY = 3;
  const displayTags = totalCount > MAX_DISPLAY ? allTags.slice(0, 2) : allTags.slice(0, MAX_DISPLAY);
  const hasMore = totalCount > MAX_DISPLAY;
  const moreCount = totalCount - 2;

  const today = isToday(date);

  return (
    <div className="flex h-full flex-col" {...(today ? { 'data-onboarding-id': 'study-big-calendar-today' } : {})}>
      <div className="mt-1 text-right text-sm" suppressHydrationWarning>
        {today ? <span className="bg-primary inline-flex h-6 w-6 items-center justify-center rounded text-white">{label}</span> : label}
      </div>

      {displayTags.length > 0 && (
        <div className="mt-1 ml-1 flex flex-col gap-1">
          {displayTags.map((event, index) => {
            const tagCode = event.resource.tagCode;
            const tagInfo = TAG_INFO[tagCode as TagKey];
            const isSolved = event.resource.type === 'solved';

            const bgColorClass = !isSolved ? 'bg-innerground-darkgray' : tagInfo ? tagInfo.bgColor : 'bg-logo';
            const textColorClass = isSolved && tagInfo ? tagInfo.textColor : 'text-only-gray';

            return (
              <div key={`${event.resource.problem.problemId}-${tagCode}-${index}`} className={`rounded px-2 py-0.5 text-xs ${textColorClass} ${bgColorClass} relative line-clamp-1`}>
                {!isSolved && <div className={`absolute top-0 left-0 h-full w-2 rounded-l ${tagInfo ? tagInfo.bgColor : 'bg-only-gray'}`}></div>}
                {tagInfo ? tagInfo.kr : event.title}
              </div>
            );
          })}
          {hasMore && <div className="bg-innerground-darkgray text-only-gray line-clamp-1 rounded px-2 py-0.5 text-xs">+{moreCount}개 더보기</div>}
        </div>
      )}
    </div>
  );
}

export function StudyBigCalendar({ studyCalendarData }: { studyCalendarData?: StudyCalendar }) {
  const { selectedDate, bigCalendarDate, setSelectedDate, setBigCalendarDate } = useStudyCalendarStore();
  const { setOpen: setCloseAppSidebar } = useSidebar();
  const { studySection } = useLayoutStore();

  const [initialDate] = useState(new Date());

  useEffect(() => {
    if (!bigCalendarDate) {
      setBigCalendarDate(initialDate);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const currentDate = bigCalendarDate || initialDate;

  useEffect(() => {
    if (selectedDate && bigCalendarDate) {
      if (!isSameMonth(selectedDate, bigCalendarDate)) {
        setBigCalendarDate(selectedDate);
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedDate]);

  const events = useMemo(() => {
    if (!studyCalendarData) return [];
    return transformToStudyCalendarEvents(studyCalendarData.monthlyData);
  }, [studyCalendarData]);

  const CustomMonthDateHeaderWrapper = useMemo(() => {
    // eslint-disable-next-line react/display-name
    return ({ date, label }: { date: Date; label: string }) => <CustomMonthDateHeader date={date} label={label} allEvents={events} />;
  }, [events]);

  const handleSelectSlot = ({ start }: { start: Date }) => {
    setSelectedDate(start);
    setCloseAppSidebar(false);
  };

  const handleBigCalendarNavigate = (newDate: Date) => {
    setBigCalendarDate(newDate);
  };

  useGlobalShortcuts({
    enabled: studySection !== null,
    shortcuts: [
      {
        key: 'ArrowLeft',
        code: 'ArrowLeft',
        alt: true,
        action: () => handleBigCalendarNavigate(subMonths(currentDate, 1)),
        description: '이전 월로 이동',
      },
      {
        key: 'ArrowRight',
        code: 'ArrowRight',
        alt: true,
        action: () => handleBigCalendarNavigate(addMonths(currentDate, 1)),
        description: '다음 월로 이동',
      },
      {
        key: 'ArrowUp',
        code: 'ArrowUp',
        alt: true,
        action: () => handleBigCalendarNavigate(subMonths(currentDate, 1)),
        description: '이전 월로 이동',
      },
      {
        key: 'ArrowDown',
        code: 'ArrowDown',
        alt: true,
        action: () => handleBigCalendarNavigate(addMonths(currentDate, 1)),
        description: '다음 월로 이동',
      },
      {
        key: 't',
        alt: true,
        action: () => handleBigCalendarNavigate(new Date()),
        description: '오늘로 이동',
      },
    ],
  });

  const lastScrollTime = useRef(0);
  const SCROLL_THROTTLE = 300;

  const handleWheel = (e: React.WheelEvent) => {
    const now = Date.now();
    if (now - lastScrollTime.current < SCROLL_THROTTLE) return;
    lastScrollTime.current = now;

    if (e.deltaY > 0) {
      handleBigCalendarNavigate(addMonths(currentDate, 1));
    } else if (e.deltaY < 0) {
      handleBigCalendarNavigate(subMonths(currentDate, 1));
    }
  };

  return (
    <div className="calendar-12px h-full w-full" onWheel={handleWheel}>
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
