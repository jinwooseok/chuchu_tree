import { ChevronLeft, ChevronRight, Leaf } from 'lucide-react';
import { ActivityCalendar, Props as CalendarProps, ThemeInput } from 'react-activity-calendar';
import { useTheme } from 'next-themes';
import { AppTooltip } from '@/components/custom/tooltip/AppTooltip';
import { useState, useMemo } from 'react';
import { useLandingStreak, useLandingUser } from '@/features/landing';

const lightTheme: ThemeInput = {
  light: ['#e4e4e4', '#A1E4AC', '#78CB94', '#4EB17C', '#007950'],
  dark: ['#e4e4e4', '#A1E4AC', '#78CB94', '#4EB17C', '#007950'],
};

const darkTheme: ThemeInput = {
  light: ['#222120', '#4EB17C', '#007950', '#025036', '#023a27'],
  dark: ['#222120', '#4EB17C', '#007950', '#025036', '#023a27'],
};

interface ActivityData {
  date: string;
  count: number;
  level: number;
}

/**
 * streaks 데이터를 ActivityCalendar 형식으로 변환
 * startDate와 endDate 범위 내의 데이터만 필터링하여 반환
 */
const transformStreaksData = (streaks: Array<{ streakDate: string; solvedCount: number; solvedLevel: number }>, startDate: string, endDate: string): ActivityData[] => {
  // streaks를 Map으로 변환 (날짜를 key로)
  const dataMap = new Map<string, ActivityData>();
  streaks.forEach((streak) => {
    // 유효한 날짜이고, startDate와 endDate 범위 내에 있는 경우만 추가
    if (streak?.streakDate && typeof streak.streakDate === 'string') {
      if (streak.streakDate >= startDate && streak.streakDate <= endDate) {
        dataMap.set(streak.streakDate, {
          date: streak.streakDate,
          count: streak.solvedCount || 0,
          level: streak.solvedLevel || 0,
        });
      }
    }
  });

  // 시작 날짜가 없으면 추가
  if (!dataMap.has(startDate)) {
    dataMap.set(startDate, { date: startDate, count: 0, level: 0 });
  }

  // 끝 날짜가 없으면 추가
  if (!dataMap.has(endDate)) {
    dataMap.set(endDate, { date: endDate, count: 0, level: 0 });
  }

  // Map을 배열로 변환하고 날짜순 정렬
  return Array.from(dataMap.values()).sort((a, b) => a.date.localeCompare(b.date));
};

export default function LandingTopStreakbar() {
  const user = useLandingUser();
  const { resolvedTheme } = useTheme();
  const currentTheme = resolvedTheme === 'dark' ? darkTheme : lightTheme;

  // 현재 보여주는 기간 상태 관리 (초기값: 오늘 기준 1년 전부터 오늘까지)
  const [dateRange, setDateRange] = useState<{ startDate: string; endDate: string }>(() => {
    const today = new Date();
    const oneYearAgo = new Date();
    oneYearAgo.setFullYear(oneYearAgo.getFullYear() - 1);
    return {
      startDate: oneYearAgo.toISOString().split('T')[0],
      endDate: today.toISOString().split('T')[0],
    };
  });

  const streaksData = useLandingStreak();

  // 이전 버튼 비활성화 여부 (오늘 기준 1년 전까지만 가능)
  const isDisabledPrev = useMemo(() => {
    const today = new Date();
    const fiveYearsAgo = new Date();
    fiveYearsAgo.setFullYear(today.getFullYear() - 3);
    const prevStartDate = new Date(dateRange.startDate);
    prevStartDate.setFullYear(prevStartDate.getFullYear() - 1);
    return prevStartDate < fiveYearsAgo;
  }, [dateRange.startDate]);

  // 다음 버튼 비활성화 여부 (오늘 기준 1년 후까지만 가능)
  const isDisabledNext = useMemo(() => {
    const today = new Date();
    const oneYearLater = new Date();
    oneYearLater.setFullYear(today.getFullYear() + 1);
    const nextEndDate = new Date(dateRange.endDate);
    nextEndDate.setFullYear(nextEndDate.getFullYear() + 1);
    return nextEndDate > oneYearLater;
  }, [dateRange.endDate]);

  // 네비게이션 버튼 핸들러
  const handleClick = (action: 'PREV' | 'NEXT') => {
    const newStartDate = new Date(dateRange.startDate);
    const newEndDate = new Date(dateRange.endDate);

    if (action === 'PREV') {
      newStartDate.setFullYear(newStartDate.getFullYear() - 1);
      newEndDate.setFullYear(newEndDate.getFullYear() - 1);
    } else {
      newStartDate.setFullYear(newStartDate.getFullYear() + 1);
      newEndDate.setFullYear(newEndDate.getFullYear() + 1);
    }
    setDateRange({
      startDate: newStartDate.toISOString().split('T')[0],
      endDate: newEndDate.toISOString().split('T')[0],
    });
  };

  // 데이터가 없거나 배열이 아니면 로딩 상태 표시
  if (!streaksData || !Array.isArray(streaksData)) {
    return (
      <div className="bg-innerground-white flex h-full items-center justify-center overflow-hidden p-4">
        <div className="text-muted-foreground text-sm">스트릭 데이터를 불러오는 중...</div>
      </div>
    );
  }

  const longestStreak = user?.bjAccount?.stat?.longestStreak || 0;
  const activityData = transformStreaksData(streaksData, dateRange.startDate, dateRange.endDate);

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
    <div className="bg-innerground-white flex h-full cursor-default items-center justify-center p-4">
      <div className="max-w-full min-w-0">
        <div className="mb-2 flex items-center justify-between">
          <div className="text-muted-foreground flex items-center gap-2 text-sm">
            <Leaf height={14} width={14} />
            스트릭
          </div>
          {/* 네비게이션 버튼 */}
          <div className="flex gap-2">
            <AppTooltip content={isDisabledPrev ? '더 이상 이전 데이터가 없습니다' : '이전으로 이동'} side="bottom">
              <button
                onClick={() => handleClick('PREV')}
                disabled={isDisabledPrev}
                className="text-muted-foreground hover:bg-background cursor-pointer rounded px-3 py-1 text-xs disabled:cursor-not-allowed disabled:opacity-40"
                aria-label="이전으로 이동"
              >
                <ChevronLeft className="h-4 w-4" />
              </button>
            </AppTooltip>
            <AppTooltip content={isDisabledNext ? '더 이상 다음 데이터가 없습니다' : '다음으로 이동'} side="bottom">
              <button
                onClick={() => handleClick('NEXT')}
                disabled={isDisabledNext}
                className="text-muted-foreground hover:bg-background cursor-pointer rounded px-3 py-1 text-xs disabled:cursor-not-allowed disabled:opacity-40"
                aria-label="다음으로 이동"
              >
                <ChevronRight className="h-4 w-4" />
              </button>
            </AppTooltip>
          </div>
        </div>
        <div className="overflow-x-auto">
          <ActivityCalendar
            data={activityData}
            blockSize={14}
            labels={labels}
            showMonthLabels
            showWeekdayLabels={['sun', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat']}
            theme={currentTheme}
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
