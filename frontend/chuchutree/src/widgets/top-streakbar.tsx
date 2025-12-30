import { Leaf } from 'lucide-react';
import { ActivityCalendar, Props as CalendarProps, ThemeInput } from 'react-activity-calendar';

const MockLongestStreak = 4;
const MockStreaks = [
  {
    problemHistoryId: 1,
    solvedCount: 1,
    solvedDate: '2025-04-07',
  },
  {
    problemHistoryId: 2,
    solvedCount: 2,
    solvedDate: '2025-04-08',
  },
  {
    problemHistoryId: 3,
    solvedCount: 3,
    solvedDate: '2025-12-09',
  },
  {
    problemHistoryId: 4,
    solvedCount: 4,
    solvedDate: '2025-12-10',
  },
  {
    problemHistoryId: 5,
    solvedCount: 5,
    solvedDate: '2025-12-11',
  },
  {
    problemHistoryId: 6,
    solvedCount: 6,
    solvedDate: '2025-12-12',
  },
  {
    problemHistoryId: 7,
    solvedCount: 9,
    solvedDate: '2025-12-20',
  },
  {
    problemHistoryId: 8,
    solvedCount: 10,
    solvedDate: '2025-12-21',
  },
];

const explicitTheme: ThemeInput = {
  light: ['#e4e4e4', '#A1E4AC', '#78CB94', '#4EB17C', '#007950'],
  dark: ['#e4e4e4', '#A1E4AC', '#78CB94', '#4EB17C', '#007950'],
};

const labels = {
  months: ['1월', '2월', '3월', '4월', '5월', '6월', '7월', '8월', '9월', '10월', '11월', '12월'],
  weekdays: ['S', 'M', 'T', 'W', 'T', 'F', 'S'],
  totalCount: `최장 ${MockLongestStreak}일 연속 문제 해결`,
  legend: {
    less: '0',
    more: '10',
  },
} satisfies CalendarProps['labels'];

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

export default function TopStreakbar() {
  return (
    <div className="bg-card flex h-full items-center justify-center overflow-hidden p-4">
      <div className="max-w-full min-w-0">
        <div className="text-muted-foreground mb-2 flex items-center gap-2 text-sm">
          <Leaf height={14} width={14} />
          스트릭
        </div>
        <div className="overflow-x-auto">
          <ActivityCalendar
            data={data}
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

/*
목데이터 => data로 변환 + count값에 따른 level 값 연동 변환 해주기
최적화: 껏다켰다할때 개느림 => 캐싱해야될듯

*/
