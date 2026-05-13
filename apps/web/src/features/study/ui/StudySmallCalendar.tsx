'use client';

import { useState } from 'react';
import Calendar from 'react-calendar';
import 'react-calendar/dist/Calendar.css';
import { useStudyCalendarStore } from '@/lib/store/studyCalendar';
import { StudyCalendar } from '@/entities/study';
import { isSameDay, isSameMonth, format } from 'date-fns';
import { ko } from 'date-fns/locale';
import { ChevronUp, ChevronDown, Undo2 } from 'lucide-react';
import { AppTooltip } from '@/components/custom/tooltip/AppTooltip';
import { getStudyProblemStatus } from '../lib/utils';

interface StudySmallCalendarProps {
  studyCalendarData?: StudyCalendar;
  activeStartDate?: Date;
  onActiveStartDateChange?: (date: Date) => void;
}

export function StudySmallCalendar({ studyCalendarData, activeStartDate: externalActiveStartDate, onActiveStartDateChange }: StudySmallCalendarProps) {
  const { selectedDate, setSelectedDate } = useStudyCalendarStore();

  const [internalActiveStartDate, setInternalActiveStartDate] = useState<Date>(selectedDate || new Date());
  const activeStartDate = externalActiveStartDate || internalActiveStartDate;
  const setActiveStartDate = onActiveStartDateChange || setInternalActiveStartDate;

  const monthlyData = studyCalendarData?.monthlyData || [];

  const handleDateChange = (value: Date | null) => {
    if (value) {
      setSelectedDate(value);
    }
  };

  const handleToday = () => {
    setActiveStartDate(new Date());
  };

  const handlePrevMonth = () => {
    const newDate = new Date(activeStartDate);
    newDate.setMonth(newDate.getMonth() - 1);
    setActiveStartDate(newDate);
  };

  const handleNextMonth = () => {
    const newDate = new Date(activeStartDate);
    newDate.setMonth(newDate.getMonth() + 1);
    setActiveStartDate(newDate);
  };

  const isCurrentMonth = isSameMonth(activeStartDate, new Date());

  // 날짜에 전원 해결한 문제가 1개 이상인지 확인 → solved-tile
  const hasSolvedProblems = (date: Date) => {
    const dateString = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
    const dayData = monthlyData.find((d) => d.targetDate === dateString);
    if (!dayData) return false;
    return dayData.problems.some((p) => getStudyProblemStatus(p) === 'solved');
  };

  // solved 문제는 없고 미해결(willSolve) 문제가 1개 이상인지 확인 → willsolve-tile
  const hasOnlyWillSolveProblems = (date: Date) => {
    const dateString = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
    const dayData = monthlyData.find((d) => d.targetDate === dateString);
    if (!dayData || dayData.problems.length === 0) return false;
    return !dayData.problems.some((p) => getStudyProblemStatus(p) === 'solved');
  };

  const tileClassName = ({ date, view }: { date: Date; view: string }) => {
    if (view === 'month') {
      const classes = ['custom-tile'];

      if (selectedDate && isSameDay(date, selectedDate)) {
        classes.push('selected-tile');
        return classes.join(' ');
      }

      const isToday = isSameDay(date, new Date());
      if (isToday) {
        classes.push('today-tile');
        return classes.join(' ');
      }

      if (hasSolvedProblems(date)) {
        classes.push('solved-tile');
      } else if (hasOnlyWillSolveProblems(date)) {
        classes.push('willsolve-tile');
      }

      return classes.join(' ');
    }
    return '';
  };

  return (
    <div className="small-calendar-wrapper">
      <div className="mb-3 flex items-center justify-between">
        {!isCurrentMonth && <div className="mt-1 text-xs font-semibold select-none">{format(activeStartDate, 'yyyy MM월', { locale: ko })}</div>}
        {isCurrentMonth && <div></div>}
        <div className="flex items-center gap-1">
          <AppTooltip content="오늘로 돌아가기" side="bottom">
            <button onClick={handleToday} className="hover:bg-background text-muted-foreground cursor-pointer rounded p-1 transition-colors" aria-label="오늘로 돌아가기">
              <Undo2 className="h-4 w-4" />
            </button>
          </AppTooltip>
          <AppTooltip content="지난달로 이동" side="bottom">
            <button onClick={handlePrevMonth} className="hover:bg-background text-muted-foreground cursor-pointer rounded p-1 transition-colors" aria-label="지난달로 이동">
              <ChevronUp className="h-4 w-4" />
            </button>
          </AppTooltip>
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
