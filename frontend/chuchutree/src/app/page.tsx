'use client';

import { SidebarInset, SidebarProvider } from '@/components/ui/sidebar';
import { LandingAppSidebar } from '@/widgets/landing/landing-app-sidebar';
import { useLayoutStore } from '@/lib/store/layout';
import { useSidebar } from '@/components/ui/sidebar';
import { useState, useEffect } from 'react';
import { useResizable } from '@/lib/hooks/useResizable';
import { ResizeHandle } from '@/components/custom/ResizeHandle';
import { cn } from '@/lib/utils';
import LandingCalendarSidebar from '@/widgets/landing/landing-calendar-sidebar';
import LandingTagSidebar from '@/widgets/landing/landing-tag-sidebar';
import LandingTopTierbar from '@/widgets/landing/landing-top-tierbar';
import LandingTopStreakbar from '@/widgets/landing/landing-top-streakbar';
import LandingMainCalendar from '@/widgets/landing/landing-main-calendar';
import LandingMainTagDashboard from '@/widgets/landing/landing-main-tag-dashboard';
import LandingBottomRecommend from '@/widgets/landing/landing-bottom-recommend';
import { OnboardingOverlay } from '@/features/landing';
import { useOnboardingStore } from '@/lib/store/onboarding';

function LandingPageContent() {
  const {
    topSection,
    centerSection,
    bottomSection,
    topSectionTierbarHeight,
    topSectionStreakHeight,
    bottomSectionHeight,
    infoSidebarWidth,
    isResizing,
    setResizing,
    setInfoSidebarWidth,
    setTopSectionTierbarHeight,
    setTopSectionStreakHeight,
    setBottomSectionHeight,
  } = useLayoutStore();
  const { state: sidebarState } = useSidebar();

  // 애니메이션 중에 이전 컴포넌트를 유지하기 위한 state
  const [prevTopSection, setPrevTopSection] = useState(topSection);
  const [prevBottomSection, setPrevBottomSection] = useState(bottomSection);

  // InfoSidebar 리사이즈
  const { size: sidebarWidth, handleMouseDown: handleSidebarResize } = useResizable({
    direction: 'horizontal',
    initialSize: infoSidebarWidth,
    minSize: 200,
    maxSize: 350,
    onResizeStart: () => setResizing(true),
    onResizeEnd: (width) => {
      setInfoSidebarWidth(width);
      setResizing(false);
    },
  });

  // TopSection 리사이즈
  const { size: topHeight, handleMouseDown: handleTopResize } = useResizable({
    direction: 'vertical',
    initialSize: topSection === 'tierbar' ? topSectionTierbarHeight : topSectionStreakHeight,
    minSize: topSection === 'streak' ? 240 : 60,
    maxSize: topSection === 'streak' ? 300 : 120,
    onResizeStart: () => setResizing(true),
    onResizeEnd: (height) => {
      if (topSection === 'tierbar') {
        setTopSectionTierbarHeight(height);
      } else if (topSection === 'streak') {
        setTopSectionStreakHeight(height);
      }
      setResizing(false);
    },
  });

  // BottomSection 리사이즈
  const { size: bottomHeight, handleMouseDown: handleBottomResize } = useResizable({
    direction: 'vertical',
    initialSize: bottomSectionHeight,
    minSize: 240,
    maxSize: 300,
    inverted: true, // bottom section은 핸들이 위쪽에 있어 드래그 방향 반전 필요
    onResizeStart: () => setResizing(true),
    onResizeEnd: (height) => {
      setBottomSectionHeight(height);
      setResizing(false);
    },
  });

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

  // 내부 컨텐츠 최소 높이
  const topInnerHeight = displayTopSection === 'tierbar' ? 'min-h-[80px]' : displayTopSection === 'streak' ? 'min-h-[240px]' : '';
  const bottomInnerHeight = displayBottomSection === 'recommend' ? 'min-h-[240px]' : '';

  // translate 계산 (슬라이드 애니메이션)
  const topTranslate = topSection !== null ? 'translate-y-0' : '-translate-y-full';
  const bottomTranslate = bottomSection === 'recommend' ? 'translate-y-0' : 'translate-y-full';

  // AppSidebar가 collapsed일 때만 InfoSidebar 표시
  const showInfoSidebar = sidebarState === 'collapsed';

  return (
    <div className="bg-background flex h-[calc(100vh-16px)] gap-2 overflow-hidden">
      {/* Info 사이드바 - AppSidebar가 닫혔을 때만 표시 */}
      {showInfoSidebar && (
        <div className={cn('relative h-full border-r', !isResizing && 'transition-all delay-200 duration-300 ease-in-out')} style={{ width: `${sidebarWidth}px` }}>
          <div className="bg-innerground-white h-full overflow-hidden">{centerSection === 'calendar' ? <LandingCalendarSidebar /> : <LandingTagSidebar />}</div>
          <ResizeHandle direction="horizontal" onMouseDown={handleSidebarResize} className="absolute top-0 right-0 h-full" />
        </div>
      )}

      {/* 메인 영역 */}
      <main className="flex min-w-0 flex-1 flex-col">
        <div
          className={cn('hide-scrollbar relative overflow-scroll', !isResizing && 'transition-all duration-300 ease-in-out')}
          style={topSection ? { height: `${topHeight}px`, marginBottom: '0.5rem' } : { height: 0 }}
        >
          <div className={cn('bg-background h-full', !isResizing && 'transition-transform duration-300 ease-in-out', topTranslate, topInnerHeight)}>
            {displayTopSection === 'tierbar' && <LandingTopTierbar />}
            {displayTopSection === 'streak' && <LandingTopStreakbar />}
          </div>
          {topSection && <ResizeHandle direction="vertical" onMouseDown={handleTopResize} className="absolute bottom-0 left-0 w-full" />}
        </div>

        <div className="flex-1 overflow-hidden transition-all duration-300 ease-in-out">{centerSection === 'calendar' ? <LandingMainCalendar /> : <LandingMainTagDashboard />}</div>

        <div
          className={cn('hide-scrollbar relative overflow-scroll', !isResizing && 'transition-all duration-300 ease-in-out')}
          style={bottomSection ? { height: `${bottomHeight}px`, marginTop: '0.5rem' } : { height: 0 }}
        >
          <div className={cn('bg-background h-full', !isResizing && 'transition-transform duration-300 ease-in-out', bottomTranslate, bottomInnerHeight)}>
            {displayBottomSection === 'recommend' && <LandingBottomRecommend />}
          </div>
          {bottomSection && <ResizeHandle direction="vertical" onMouseDown={handleBottomResize} className="absolute top-0 left-0 w-full" />}
        </div>
      </main>
    </div>
  );
}

export default function LandingPage() {
  const { hasCompletedOnboarding, isActive, _hasHydrated, startOnboarding } = useOnboardingStore();

  // 최초 진입자 감지 및 자동 실행 (hydration 완료 후에만 실행)
  useEffect(() => {
    if (_hasHydrated && !hasCompletedOnboarding && !isActive) {
      console.log('온보딩 시작:', hasCompletedOnboarding, isActive);
      startOnboarding();
    }
  }, [_hasHydrated, hasCompletedOnboarding, isActive, startOnboarding]);

  return (
    <SidebarProvider defaultOpen={false}>
      <LandingAppSidebar />
      <SidebarInset>
        <LandingPageContent />
      </SidebarInset>
      {/* 온보딩 오버레이 */}
      {isActive && <OnboardingOverlay />}
    </SidebarProvider>
  );
}
