import { useCalendar } from '@/entities/calendar';
import { useGetBannedProblems } from '@/entities/recommendation';
import { useTagDashboard } from '@/entities/tag-dashboard';
import { RecommendationAnswer, RecommendationButton } from '@/features/recommendation';
import { getLevelColorClasses, getDaysAgo } from '@/features/tag-dashboard/lib/utils';
import { useCalendarStore } from '@/lib/store/calendar';
import { useMemo } from 'react';

export default function BottomRecommend() {
  const { selectedDate } = useCalendarStore();
  const year = selectedDate?.getFullYear() || new Date().getFullYear();
  const month = (selectedDate?.getMonth() || new Date().getMonth()) + 1;
  const { data: calendarData } = useCalendar(year, month);
  const { data: bannedListData } = useGetBannedProblems();
  const { data: tagDashboard } = useTagDashboard();

  const tagLevelMap = useMemo(() => {
    if (!tagDashboard) return undefined;
    return Object.fromEntries(
      tagDashboard.tags.map((tag) => {
        const { excludedYn, accountStat } = tag;
        const levelStr = !excludedYn ? accountStat.currentLevel : 'EXCLUDED';
        const bg = !excludedYn ? getLevelColorClasses(accountStat.currentLevel).bg : 'bg-excluded-bg';
        const daysAgo = accountStat.lastSolvedDate !== null ? getDaysAgo(accountStat.lastSolvedDate) : null;
        return [
          tag.tagCode,
          {
            bg,
            char: levelStr.charAt(0),
            level: levelStr,
            daysAgo,
            isOverdue: daysAgo !== null && accountStat.recommendation_period < daysAgo,
            solvedProblemCount: accountStat.solvedProblemCount,
          },
        ];
      }),
    );
  }, [tagDashboard]);

  return (
    <div className="bg-innerground-white flex h-full items-center justify-between p-4" data-onboarding-id="bottom-recommend">
      <RecommendationButton tagLevelMap={tagLevelMap} />
      <RecommendationAnswer calendarData={calendarData} bannedListData={bannedListData} />
    </div>
  );
}
