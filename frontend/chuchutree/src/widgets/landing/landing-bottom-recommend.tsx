import { useLandingBannedList, useLandingCalendar } from '@/features/landing';
import { RecommendationAnswer, RecommendationButton } from '@/features/recommendation';

export default function LandingBottomRecommend() {
  const calendarData = useLandingCalendar();
  const bannedListData = useLandingBannedList();
  return (
    <div className="bg-innerground-white flex h-full items-center justify-between p-4">
      <RecommendationButton isLanding={true} />
      <RecommendationAnswer isLanding={true} calendarData={calendarData} bannedListData={bannedListData}/>
    </div>
  );
}
