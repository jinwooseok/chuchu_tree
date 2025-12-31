import SmallCalendar from '@/features/calendar/ui/SmallCalendar';

export default function CalendarSidebar() {
  return (
    <div className="flex h-full flex-col p-4">
      <SmallCalendar />
      <div className="text-xs">나머지 아래내용</div>
      <div>나머지 아래내용</div>
      <div>나머지 아래내용</div>
    </div>
  );
}
