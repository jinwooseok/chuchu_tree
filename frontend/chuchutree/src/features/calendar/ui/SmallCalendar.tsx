'use client';

import Calendar from 'react-calendar';
import 'react-calendar/dist/Calendar.css';
import { useCalendarStore } from '@/lib/store/calendar';
import { isSameDay } from 'date-fns';

export default function SmallCalendar() {
  const selectedDate = useCalendarStore((state) => state.selectedDate);
  const setSelectedDate = useCalendarStore((state) => state.setSelectedDate);
  const monthlyData = useCalendarStore((state) => state.monthlyData);

  // 날짜 클릭 핸들러
  const handleDateChange = (value: Date | null) => {
    if (value) {
      setSelectedDate(value);
    }
  };

  // 특정 날짜에 문제가 있는지 확인
  const hasProblems = (date: Date) => {
    const dateString = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
    const dayData = monthlyData.find((data) => data.date === dateString);
    return dayData && (dayData.solvedProblemCount > 0 || dayData.willSolveProblemCount > 0);
  };

  // 타일에 커스텀 클래스 추가
  const tileClassName = ({ date, view }: { date: Date; view: string }) => {
    if (view === 'month') {
      const classes = [];

      // 문제가 있는 날짜
      if (hasProblems(date)) {
        classes.push('has-problems');
      }

      // 선택된 날짜
      if (isSameDay(date, selectedDate)) {
        classes.push('selected-date');
      }

      return classes.join(' ');
    }
    return '';
  };

  // 타일에 컨텐츠 추가 (문제가 있는 날짜에 점 표시)
  const tileContent = ({ date, view }: { date: Date; view: string }) => {
    if (view === 'month' && hasProblems(date)) {
      return <div className="problem-dot"></div>;
    }
    return null;
  };

  return (
    <div className="small-calendar-wrapper">
      <style jsx global>{`
        .small-calendar-wrapper .react-calendar {
          width: 100%;
          border: none;
          font-family: inherit;
        }

        .small-calendar-wrapper .react-calendar__tile {
          position: relative;
          padding: 0.5rem;
          font-size: 0.875rem;
        }

        .small-calendar-wrapper .react-calendar__tile.has-problems {
          background-color: #f3f4f6;
        }

        .small-calendar-wrapper .react-calendar__tile.selected-date {
          background-color: #3b82f6 !important;
          color: white !important;
        }

        .small-calendar-wrapper .react-calendar__tile:hover {
          background-color: #e5e7eb;
        }

        .small-calendar-wrapper .react-calendar__tile.selected-date:hover {
          background-color: #2563eb !important;
        }

        .small-calendar-wrapper .react-calendar__tile--now {
          background-color: #fef3c7;
        }

        .small-calendar-wrapper .react-calendar__tile--now.selected-date {
          background-color: #3b82f6 !important;
        }

        .small-calendar-wrapper .problem-dot {
          position: absolute;
          bottom: 4px;
          left: 50%;
          transform: translateX(-50%);
          width: 4px;
          height: 4px;
          background-color: #3b82f6;
          border-radius: 50%;
        }

        .small-calendar-wrapper .react-calendar__tile.selected-date .problem-dot {
          background-color: white;
        }
      `}</style>

      <Calendar
        onChange={(value) => handleDateChange(value as Date)}
        value={selectedDate}
        locale="ko-KR"
        formatDay={(locale, date) => String(date.getDate())}
        tileClassName={tileClassName}
        tileContent={tileContent}
        prev2Label={null}
        next2Label={null}
      />
    </div>
  );
}
