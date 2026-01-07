import { CalendarEvent } from '@/entities/calendar';
import { TAG_INFO } from '@/shared/constants/tagSystem';
import { getDisplayTags } from '../lib/utils';
import { DateCellWrapperProps } from 'react-big-calendar';

interface CustomDateCellProps extends DateCellWrapperProps {
  events: CalendarEvent[];
}

export default function CustomDateCell({ children, value, events }: CustomDateCellProps) {
  // 현재 날짜(value)에 해당하는 이벤트들만 필터링
  const dayEvents = events.filter((event) => {
    const eventDate = new Date(event.start);
    const cellDate = new Date(value);
    return eventDate.getFullYear() === cellDate.getFullYear() && eventDate.getMonth() === cellDate.getMonth() && eventDate.getDate() === cellDate.getDate();
  });

  const { displayTags, hasMore, moreCount } = getDisplayTags(dayEvents);

  return (
    <div className="relative h-full">
      {children}
      {displayTags.length > 0 && (
        <div className="mt-1 flex flex-col gap-1 px-1">
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
