'use client';

import { useLayoutStore } from '@/lib/store/layout';
import { useSidebar } from '@/components/ui/sidebar';
import InfoSidebar from '@/widgets/info-sidebar';
import MainCalendar from '@/widgets/main-calendar';
import MainTagDashboard from '@/widgets/main-tag-dashboard';
import TopTierbar from '@/widgets/top-tierbar';
import TopStreakbar from '@/widgets/top-streakbar';
import BottomRecommend from '@/widgets/bottom-recommend';

export default function DashboardLayout() {
  const { topSection, centerSection, bottomSection } = useLayoutStore();
  const { state: sidebarState } = useSidebar();

  // 상단 영역 높이 계산
  const topHeight = topSection === 'tierbar' ? 'h-1/6 min-h-[80px] mb-2' : topSection === 'streak' ? 'h-1/3 min-h-[240px] mb-2' : 'h-0';

  // 하단 영역 높이 계산
  const bottomHeight = bottomSection === 'recommend' ? 'h-1/3 min-h-[200px] mt-2' : 'h-0';

  // AppSidebar가 collapsed일 때만 InfoSidebar 표시
  const showInfoSidebar = sidebarState === 'collapsed';

  return (
    <div className="bg-background flex h-full gap-2 overflow-hidden">
      {/* Info 사이드바 - AppSidebar가 닫혔을 때만 표시 */}
      {showInfoSidebar && <InfoSidebar />}

      {/* 메인 영역 */}
      <main className="flex min-w-0 flex-1 flex-col">
        {/* 상단 영역 (티어바/스트릭) */}
        <div className={`transition-all duration-300 ease-in-out ${topHeight} overflow-hidden`}>
          {topSection === 'tierbar' && <TopTierbar />}
          {topSection === 'streak' && <TopStreakbar />}
        </div>

        {/* 중앙 영역 (캘린더/태그 대시보드) */}
        <div className="flex-1 overflow-hidden">{centerSection === 'calendar' ? <MainCalendar /> : <MainTagDashboard />}</div>

        {/* 하단 영역 (문제 추천) */}
        <div className={`transition-all duration-300 ease-in-out ${bottomHeight} overflow-hidden`}>{bottomSection === 'recommend' && <BottomRecommend />}</div>
      </main>
    </div>
  );
}
