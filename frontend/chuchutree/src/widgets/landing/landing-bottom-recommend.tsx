import { useLandingBannedList, useLandingCalendar } from '@/features/landing';
import { RecommendationAnswer, RecommendationButton } from '@/features/recommendation';
import { useCalendarStore } from '@/lib/store/calendar';

export default function LandingBottomRecommend() {
  const { selectedDate } = useCalendarStore();
  const year = selectedDate?.getFullYear() || new Date().getFullYear();
  const month = (selectedDate?.getMonth() || new Date().getMonth()) + 1;
  const calendarData = useLandingCalendar({ year: year, month: month });
  const bannedListData = useLandingBannedList();
  return (
    <div className="bg-innerground-white flex h-full items-center justify-between p-4">
      <RecommendationButton isLanding={true} />
      <RecommendationAnswer isLanding={true} calendarData={calendarData} bannedListData={bannedListData} />
    </div>
  );
}
