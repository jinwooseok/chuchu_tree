'use client';

import { useState, useEffect } from 'react';
import Calendar from 'react-calendar';
import 'react-calendar/dist/Calendar.css';
import { useCalendarStore } from '@/lib/store/calendar';
import { useCalendar, Calendar as CalendarType } from '@/entities/calendar';
import { isSameDay, isSameMonth, format } from 'date-fns';
import { ko } from 'date-fns/locale';
import { ChevronUp, ChevronDown, Undo2 } from 'lucide-react';
import { AppTooltip } from '@/components/custom/tooltip/AppTooltip';

interface MonthlyData {
  targetDate: string;
  solvedProblemCount: number;
  willSolveProblemCount: number;
}

interface SmallCalendarProps {
  calendarData?: CalendarType;
  activeStartDate?: Date;
  onActiveStartDateChange?: (date: Date) => void;
}

export function SmallCalendar({ calendarData, activeStartDate: externalActiveStartDate, onActiveStartDateChange }: SmallCalendarProps) {
  const { selectedDate, setSelectedDate } = useCalendarStore();

  // activeStartDate가 props로 제공되면 사용, 아니면 내부 상태로 관리
  const [internalActiveStartDate, setInternalActiveStartDate] = useState<Date>(selectedDate || new Date());
  const activeStartDate = externalActiveStartDate || internalActiveStartDate;
  const setActiveStartDate = onActiveStartDateChange || setInternalActiveStartDate;

  // calendarData에서 직접 monthlyData 사용
  const monthlyData = calendarData?.monthlyData || [];

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

      // 선택된 날짜 - 최우선 (오늘이든 아니든 선택되면 selected-tile)
      if (selectedDate && isSameDay(date, selectedDate)) {
        classes.push('selected-tile');
        return classes.join(' ');
      }

      // 오늘 날짜 - 선택되지 않았을 때만
      const isToday = isSameDay(date, new Date());
      if (isToday) {
        classes.push('today-tile');
        return classes.join(' ');
      }

      // solved 문제가 있는 날짜
      if (hasSolvedProblems(date)) {
        classes.push('solved-tile');
      }
      // solved 없고 will solve만 있는 날짜
      else if (hasOnlyWillSolveProblems(date)) {
        classes.push('willsolve-tile');
      }

      return classes.join(' ');
    }
    return '';
  };

  return (
    <div className="small-calendar-wrapper">
      {/* 커스텀 네비게이션 */}
      <div className="mb-3 flex items-center justify-between">
        {/* 현재 월이 오늘이 포함된 월이 아닐 때만 년월 표시 */}
        {!isCurrentMonth && <div className="mt-1 text-xs font-semibold select-none">{format(activeStartDate, 'yyyy MM월', { locale: ko })}</div>}
        {isCurrentMonth && <div></div>}
        {/* 네비게이션 버튼 */}
        <div className="flex items-center gap-1">
          {/* 오늘로 이동 */}
          <AppTooltip content="오늘로 돌아가기" side="bottom">
            <button onClick={handleToday} className="hover:bg-background text-muted-foreground cursor-pointer rounded p-1 transition-colors" aria-label="오늘로 돌아가기">
              <Undo2 className="h-4 w-4" />
            </button>
          </AppTooltip>
          {/* 이전달 */}
          <AppTooltip content="지난달로 이동" side="bottom">
            <button onClick={handlePrevMonth} className="hover:bg-background text-muted-foreground cursor-pointer rounded p-1 transition-colors" aria-label="지난달로 이동">
              <ChevronUp className="h-4 w-4" />
            </button>
          </AppTooltip>
          {/* 다음달 */}
          <AppTooltip content="다음 달로 이동" side="bottom">
            <button onClick={handleNextMonth} className="hover:bg-background text-muted-foreground cursor-pointer rounded p-1 transition-colors" aria-label="다음 달로 이동">
              <ChevronDown className="h-4 w-4" />
            </button>
          </AppTooltip>
        </div>
      </div>

      <Calendar
        onChange={(value) => handleDateChange(value as Date)}
        value={selectedDate || new Date()}
        activeStartDate={activeStartDate}
        calendarType="gregory"
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
