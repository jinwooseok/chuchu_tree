import { useUser } from '@/entities/user/model/queries';
import { Leaf } from 'lucide-react';
import { ActivityCalendar, Props as CalendarProps, ThemeInput } from 'react-activity-calendar';

const explicitTheme: ThemeInput = {
  light: ['#e4e4e4', '#A1E4AC', '#78CB94', '#4EB17C', '#007950'],
  dark: ['#e4e4e4', '#A1E4AC', '#78CB94', '#4EB17C', '#007950'],
};

interface ActivityData {
  date: string;
  count: number;
  level: number;
}

const data = [
  {
    date: '2025-01-01',
    count: 0,
    level: 0,
  },
  {
    date: '2025-02-20',
    count: 2,
    level: 1,
  },
  {
    date: '2025-02-21',
    count: 16,
    level: 2,
  },
  {
    date: '2025-02-22',
    count: 16,
    level: 3,
  },
  {
    date: '2025-02-23',
    count: 16,
    level: 4,
  },
  {
    date: '2025-12-30',
    count: 0,
    level: 4,
  },
];

/**
 * streaks 데이터를 ActivityCalendar 형식으로 변환
 * 오늘 날짜와 1년 전 날짜가 없으면 추가
 */
const transformStreaksData = (streaks: Array<{ streakDate: string; solvedCount: number; solvedLevel: number }>): ActivityData[] => {
  // 오늘 날짜 (YYYY-MM-DD)
  const today = new Date().toISOString().split('T')[0];

  // 정확히 1년 전 날짜
  const oneYearAgo = new Date();
  oneYearAgo.setFullYear(oneYearAgo.getFullYear() - 1);
  const oneYearAgoDate = oneYearAgo.toISOString().split('T')[0];

  // streaks를 Map으로 변환 (날짜를 key로)
  const dataMap = new Map<string, ActivityData>();
  streaks.forEach((streak) => {
    // solvedDate가 유효한 경우만 추가 (방어 코드)
    if (streak?.streakDate && typeof streak.streakDate === 'string') {
      dataMap.set(streak.streakDate, {
        date: streak.streakDate,
        count: streak.solvedCount || 0,
        level: streak.solvedLevel || 0,
      });
    }
  });

  // 오늘 날짜가 없으면 추가
  if (!dataMap.has(today)) {
    dataMap.set(today, { date: today, count: 0, level: 0 });
  }

  // 1년 전 날짜가 없으면 추가
  if (!dataMap.has(oneYearAgoDate)) {
    dataMap.set(oneYearAgoDate, { date: oneYearAgoDate, count: 0, level: 0 });
  }

  // Map을 배열로 변환하고 날짜순 정렬
  return Array.from(dataMap.values()).sort((a, b) => a.date.localeCompare(b.date));
};

export default function TopStreakbar() {
  const { data: user } = useUser();

  // 데이터가 없거나 배열이 아니면 로딩 상태 표시
  if (!user?.bjAccount?.streaks || !Array.isArray(user.bjAccount.streaks)) {
    return (
      <div className="bg-innerground-white flex h-full items-center justify-center overflow-hidden p-4">
        <div className="text-muted-foreground text-sm">스트릭 데이터를 불러오는 중...</div>
      </div>
    );
  }

  const longestStreak = user.bjAccount.stat.longestStreak || 0;
  const activityData = transformStreaksData(user.bjAccount.streaks);

  const labels = {
    months: ['1월', '2월', '3월', '4월', '5월', '6월', '7월', '8월', '9월', '10월', '11월', '12월'],
    weekdays: ['S', 'M', 'T', 'W', 'T', 'F', 'S'],
    totalCount: `최장 ${longestStreak}일 연속 문제 해결`,
    legend: {
      less: '0',
      more: '10',
    },
  } satisfies CalendarProps['labels'];

  return (
    <div className="bg-innerground-white flex h-full items-center justify-center overflow-hidden p-4">
      <div className="max-w-full min-w-0">
        <div className="text-muted-foreground mb-2 flex items-center gap-2 text-sm">
          <Leaf height={14} width={14} />
          스트릭
        </div>
        <div className="overflow-x-auto">
          <ActivityCalendar
            data={activityData}
            blockSize={14}
            labels={labels}
            showMonthLabels
            showWeekdayLabels={['sun', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat']}
            theme={explicitTheme}
            tooltips={{
              activity: {
                text: (activity) => `${activity.date}: ${activity.count}문제 해결`,
                placement: 'bottom',
                offset: 6,
                hoverRestMs: 100,
                transitionStyles: {
                  duration: 50,
                  common: { fontSize: 12, backgroundColor: '#2d2d2d', padding: 4, color: '#f3f0f0', borderRadius: 4, paddingLeft: 24, paddingRight: 24 },
                },
                withArrow: true,
              },
            }}
          />
        </div>
      </div>
    </div>
  );
}
