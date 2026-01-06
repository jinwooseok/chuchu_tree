'use client';

import { useState, useEffect } from 'react';
import Calendar from 'react-calendar';
import 'react-calendar/dist/Calendar.css';
import { useCalendarStore } from '@/lib/store/calendar';
import { useCalendar } from '@/entities/calendar';
import { isSameDay, isSameMonth, format } from 'date-fns';
import { ko } from 'date-fns/locale';
import { ChevronUp, ChevronDown, Undo2 } from 'lucide-react';

export default function SmallCalendar() {
  const { selectedDate, monthlyData, actions } = useCalendarStore();
  const { setSelectedDate, setCalendarData } = actions;

  // 현재 표시중인 월 관리 (selectedDate가 null이면 오늘 날짜 사용)
  const [activeStartDate, setActiveStartDate] = useState<Date>(selectedDate || new Date());

  // 현재 표시 중인 월의 year/month
  const year = activeStartDate.getFullYear();
  const month = activeStartDate.getMonth() + 1;

  // 해당 월의 calendar 데이터 fetch
  const { data: calendarData } = useCalendar(year, month);

  // 데이터가 로드되면 store에 저장
  useEffect(() => {
    if (calendarData) {
      setCalendarData(calendarData);
    }
  }, [calendarData, setCalendarData]);

  // 날짜 클릭 핸들러
  const handleDateChange = (value: Date | null) => {
    if (value) {
      setSelectedDate(value);
    }
  };

  // 오늘로 이동
  const handleToday = () => {
    const today = new Date();
    setActiveStartDate(today);
    setSelectedDate(today);
  };

  // 이전달로 이동
  const handlePrevMonth = () => {
    const newDate = new Date(activeStartDate);
    newDate.setMonth(newDate.getMonth() - 1);
    setActiveStartDate(newDate);
  };

  // 다음달로 이동
  const handleNextMonth = () => {
    const newDate = new Date(activeStartDate);
    newDate.setMonth(newDate.getMonth() + 1);
    setActiveStartDate(newDate);
  };

  // 현재 월이 오늘이 포함된 월인지 확인
  const isCurrentMonth = isSameMonth(activeStartDate, new Date());

  // 특정 날짜에 solved 문제가 있는지 확인
  const hasSolvedProblems = (date: Date) => {
    const dateString = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
    const dayData = monthlyData.find((data) => data.targetDate === dateString);
    return dayData && dayData.solvedProblemCount > 0;
  };

  // 특정 날짜에 will solve 문제만 있는지 확인
  const hasOnlyWillSolveProblems = (date: Date) => {
    const dateString = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
    const dayData = monthlyData.find((data) => data.targetDate === dateString);
    return dayData && dayData.solvedProblemCount === 0 && dayData.willSolveProblemCount > 0;
  };

  // 타일에 커스텀 클래스 추가
  const tileClassName = ({ date, view }: { date: Date; view: string }) => {
    if (view === 'month') {
      const classes = ['custom-tile'];

      // 오늘 날짜
      const isToday = isSameDay(date, new Date());
      if (isToday) {
        classes.push('today-tile');
      }

      // solved 문제가 있는 날짜
      if (hasSolvedProblems(date)) {
        classes.push('solved-tile');
      }
      // solved 없고 will solve만 있는 날짜
      else if (hasOnlyWillSolveProblems(date)) {
        classes.push('willsolve-tile');
      }

      // 선택된 날짜
      if (selectedDate && isSameDay(date, selectedDate)) {
        classes.push('selected-tile');
      }

      return classes.join(' ');
    }
    return '';
  };

  return (
    <div className="small-calendar-wrapper">
      <style jsx global>{`
        .small-calendar-wrapper .react-calendar {
          width: 100%;
          border: none;
          font-family: inherit;
          background-color: transparent;
        }

        /* 기본 네비게이션 숨기기 */
        .small-calendar-wrapper .react-calendar__navigation {
          display: none;
        }

        /* 요일 헤더 스타일 */
        .small-calendar-wrapper .react-calendar__month-view__weekdays {
          font-size: 0.75rem; /* text-xs */
          color: #6b7280; /* text-muted-foreground */
          font-weight: normal;
          user-select: none; /* select-none */
        }

        .small-calendar-wrapper .react-calendar__month-view__weekdays__weekday {
          padding: 0.5rem 0.25rem;
          text-align: center;
        }

        .small-calendar-wrapper .react-calendar__month-view__weekdays__weekday abbr {
          text-decoration: none;
        }

        /* 타일 기본 스타일 */
        .small-calendar-wrapper .react-calendar__tile {
          position: relative;
          padding: 0.25rem; /* 패딩 줄임 */
          font-size: 0.75rem; /* text-xs */
          border: none;
          background: transparent;
          aspect-ratio: 1;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        /* 타일 내부 컨텐츠 (실제 숫자) */
        .small-calendar-wrapper .react-calendar__tile abbr {
          width: 100%;
          height: 100%;
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 0.25rem; /* 내부 패딩으로 여백 확보 */
        }

        /* 다른 달의 날짜 */
        .small-calendar-wrapper .react-calendar__month-view__days__day--neighboringMonth {
          color: #d1d5db;
        }

        /* 오늘 날짜 - 빨간 배경 + rounded */
        .small-calendar-wrapper .custom-tile.today-tile abbr {
          background-color: #ed6e6e;
          color: white;
          border-radius: 50%;
        }

        /* solved가 있는 날짜 */
        .small-calendar-wrapper .custom-tile.solved-tile abbr {
          background-color: #79ab7c; /* bg-advanced-bg */
          border-radius: 50%;
        }

        /* will solve만 있는 날짜 */
        .small-calendar-wrapper .custom-tile.willsolve-tile abbr {
          background-color: #e4e4e4; /* bg-innerground-darkgray */
          border-radius: 50%;
        }

        /* 선택된 날짜 (bg-imediated-bg 배경색) */
        .small-calendar-wrapper .custom-tile.selected-tile abbr {
          background-color: #f9b473 !important; /* bg-imediated-bg */
          border-radius: 50%;
        }

        /* hover 효과 - 동그란 영역에만 회색 배경 */
        .small-calendar-wrapper .react-calendar__tile:enabled:hover {
          background-color: transparent;
        }

        .small-calendar-wrapper .react-calendar__tile:enabled:hover abbr {
          background-color: rgba(0, 0, 0, 0.05);
          border-radius: 50%;
        }

        /* focus 스타일 제거 */
        .small-calendar-wrapper .react-calendar__tile:enabled:focus,
        .small-calendar-wrapper .react-calendar__tile:enabled:focus abbr {
          background-color: transparent;
          outline: none;
        }

        /* 오늘 날짜는 기본 스타일 제거 */
        .small-calendar-wrapper .react-calendar__tile--now {
          background: transparent;
        }

        .small-calendar-wrapper .react-calendar__tile--now abbr {
          /* 오늘 날짜 텍스트 스타일은 today-tile에서 처리 */
        }
      `}</style>

      {/* 커스텀 네비게이션 */}
      <div className="mb-3 flex items-center justify-between">
        {/* 현재 월이 오늘이 포함된 월이 아닐 때만 년월 표시 */}
        {!isCurrentMonth && <div className="mt-1 text-xs font-semibold select-none">{format(activeStartDate, 'yyyy MM월', { locale: ko })}</div>}
        {isCurrentMonth && <div></div>}

        <div className="flex items-center gap-1">
          {/* 오늘로 이동 */}
          <button onClick={handleToday} className="hover:bg-background text-muted-foreground cursor-pointer rounded p-1 transition-colors" title="오늘로 돌아가기">
            <Undo2 className="h-4 w-4" />
          </button>
          {/* 이전달 */}
          <button onClick={handlePrevMonth} className="hover:bg-background text-muted-foreground cursor-pointer rounded p-1 transition-colors" title="지난달로 이동">
            <ChevronUp className="h-4 w-4" />
          </button>
          {/* 다음달 */}
          <button onClick={handleNextMonth} className="hover:bg-background text-muted-foreground cursor-pointer rounded p-1 transition-colors" title="다음 달로 이동">
            <ChevronDown className="h-4 w-4" />
          </button>
        </div>
      </div>

      <Calendar
        onChange={(value) => handleDateChange(value as Date)}
        value={selectedDate || new Date()}
        activeStartDate={activeStartDate}
        onActiveStartDateChange={({ activeStartDate }) => activeStartDate && setActiveStartDate(activeStartDate)}
        locale="ko-KR"
        formatDay={(locale, date) => String(date.getDate())}
        formatShortWeekday={(locale, date) => ['일', '월', '화', '수', '목', '금', '토'][date.getDay()]}
        tileClassName={tileClassName}
        showNavigation={false}
        prev2Label={null}
        next2Label={null}
      />
    </div>
  );
}
