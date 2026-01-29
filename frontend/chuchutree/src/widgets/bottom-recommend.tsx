import { useCalendar } from '@/entities/calendar';
import { useGetBannedProblems } from '@/entities/recommendation';
import { RecommendationAnswer, RecommendationButton } from '@/features/recommendation';
import { useCalendarStore } from '@/lib/store/calendar';

export default function BottomRecommend() {
  const { selectedDate } = useCalendarStore();
  const year = selectedDate?.getFullYear() || new Date().getFullYear();
  const month = (selectedDate?.getMonth() || new Date().getMonth()) + 1;
  const { data: calendarData } = useCalendar(year, month);
  const { data: bannedListData } = useGetBannedProblems();
  return (
    <div className="bg-innerground-white flex h-full items-center justify-between p-4">
      <RecommendationButton />
      <RecommendationAnswer calendarData={calendarData} bannedListData={bannedListData} />
    </div>
  );
}
