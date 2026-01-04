'use client';

import { useLayoutStore } from '@/lib/store/layout';
import { useSidebar } from '@/components/ui/sidebar';
import { useState } from 'react';
import InfoSidebar from '@/widgets/info-sidebar';
import MainCalendar from '@/widgets/main-calendar';
import MainTagDashboard from '@/widgets/main-tag-dashboard';
import TopTierbar from '@/widgets/top-tierbar';
import TopStreakbar from '@/widgets/top-streakbar';
import BottomRecommend from '@/widgets/bottom-recommend';

export default function DashboardLayout() {
  const { topSection, centerSection, bottomSection } = useLayoutStore();
  const { state: sidebarState } = useSidebar();

  // 애니메이션 중에 이전 컴포넌트를 유지하기 위한 state
  const [prevTopSection, setPrevTopSection] = useState(topSection);
  const [prevBottomSection, setPrevBottomSection] = useState(bottomSection);

  // 렌더링 중에 조건부로 state 업데이트 (topSection이 null이 아닐 때만)
  if (topSection !== null && topSection !== prevTopSection) {
    setPrevTopSection(topSection);
  }
  if (bottomSection !== null && bottomSection !== prevBottomSection) {
    setPrevBottomSection(bottomSection);
  }

  // 표시할 섹션 결정 (현재 값이 null이면 이전 값 사용)
  const displayTopSection = topSection !== null ? topSection : prevTopSection;
  const displayBottomSection = bottomSection !== null ? bottomSection : prevBottomSection;

  // 상단 영역 높이 계산
  const topHeight = topSection === 'tierbar' ? 'h-1/6 mb-2' : topSection === 'streak' ? 'h-1/3 mb-2' : 'h-0';
  const topInnerHeight = displayTopSection === 'tierbar' ? 'min-h-[80px]' : displayTopSection === 'streak' ? 'min-h-[240px]' : '';

  // 하단 영역 높이 계산
  const bottomHeight = bottomSection === 'recommend' ? 'h-1/3 ' : 'h-0';
  const bottomInnerHeight = displayBottomSection === 'recommend' ? 'min-h-[240px]' : '';

  // translate 계산 (슬라이드 애니메이션)
  const topTranslate = topSection !== null ? 'translate-y-0' : '-translate-y-full';
  const bottomTranslate = bottomSection === 'recommend' ? 'translate-y-0' : 'translate-y-full';

  // AppSidebar가 collapsed일 때만 InfoSidebar 표시
  const showInfoSidebar = sidebarState === 'collapsed';

  return (
    <div className="bg-background flex h-[calc(100vh-16px)] gap-2 overflow-hidden">
      {/* Info 사이드바 - AppSidebar가 닫혔을 때만 표시 */}
      {showInfoSidebar && <InfoSidebar />}

      {/* 메인 영역 */}
      <main className="flex min-w-0 flex-1 flex-col">
        {/* 상단 영역 (티어바/스트릭) */}
        <div className={`transition-all duration-300 ease-in-out ${topHeight} overflow-hidden`}>
          <div className={`bg-background h-full transition-transform duration-300 ease-in-out ${topTranslate} ${topInnerHeight}`}>
            {displayTopSection === 'tierbar' && <TopTierbar />}
            {displayTopSection === 'streak' && <TopStreakbar />}
          </div>
        </div>

        {/* 중앙 영역 (캘린더/태그 대시보드) */}
        <div className="flex-1 overflow-hidden transition-all duration-300 ease-in-out">{centerSection === 'calendar' ? <MainCalendar /> : <MainTagDashboard />}</div>

        {/* 하단 영역 (문제 추천) */}
        <div className={`transition-all duration-300 ease-in-out ${bottomHeight} overflow-hidden`}>
          <div className={`bg-background h-full transition-transform duration-300 ease-in-out ${bottomTranslate} ${bottomInnerHeight}`}>
            {displayBottomSection === 'recommend' && <BottomRecommend />}
          </div>
        </div>
      </main>
    </div>
  );
}
