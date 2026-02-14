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
import { OnboardingController } from '@/features/landing';
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

export default function LandingPageClient() {
  const { hasCompletedOnboarding, isActive, _hasHydrated, startOnboarding } = useOnboardingStore();

  // 최초 진입자 감지 및 자동 실행 (hydration 완료 후에만 실행)
  useEffect(() => {
    if (_hasHydrated && !hasCompletedOnboarding && !isActive) {
      startOnboarding();
    }
  }, [_hasHydrated, hasCompletedOnboarding, isActive, startOnboarding]);

  return (
    <>
      {/* SEO 전용 콘텐츠 - 검색 엔진 최적화를 위한 구조화된 텍스트 */}
      <header className="sr-only">
        <h1>ChuChuTree - 백준 알고리즘 학습 캘린더</h1>

        <section>
          <h2>서비스 소개</h2>
          <p>
            ChuChuTree는 백준 온라인 저지와 solved.ac의 데이터를 분석하여 개인 맞춤형 알고리즘 문제를 추천하는 학습 캘린더 서비스입니다.
            알고리즘 문제 풀이 기록을 시각화하고, 취약한 알고리즘 유형을 파악하여 효율적인 학습 경로를 제시합니다.
            코딩테스트 준비생, PS 학습자, 알고리즘 공부를 시작하는 모든 분들을 위한 최적의 학습 도우미입니다.
          </p>
        </section>

        <section>
          <h2>주요 기능</h2>
          <ul>
            <li>개인 맞춤형 알고리즘 문제 추천 - 풀이 기록과 취약 유형을 분석하여 최적의 문제를 추천합니다</li>
            <li>알고리즘 유형별 대시보드 - 60여 개의 알고리즘 유형별 실력을 한눈에 확인하고 관리할 수 있습니다</li>
            <li>월별 학습 기록 캘린더 - Notion 스타일의 직관적인 캘린더로 학습 기록을 시각화합니다</li>
            <li>백준 티어 진행도 관리 - solved.ac 티어 시스템 기반으로 목표를 설정하고 진행도를 추적합니다</li>
            <li>학습 스트릭 히트맵 - 1년 단위의 학습 연속성을 히트맵으로 확인하며 동기부여를 얻습니다</li>
            <li>문제 일정 관리 - 풀고 싶은 문제를 캘린더에 등록하고 체계적으로 관리할 수 있습니다</li>
          </ul>
        </section>

        <section>
          <h2>이런 분들께 추천합니다</h2>
          <ul>
            <li>코딩테스트를 준비하는 취업 준비생</li>
            <li>알고리즘 실력을 체계적으로 키우고 싶은 학생</li>
            <li>매일 꾸준히 PS 공부를 하고 싶은 개발자</li>
            <li>백준 문제 중 어떤 유형을 공부해야 할지 모르는 초보자</li>
            <li>solved.ac 티어를 효율적으로 올리고 싶은 학습자</li>
          </ul>
        </section>

        <section>
          <h2>주요 알고리즘 유형</h2>
          <p>
            ChuChuTree는 구현, 그리디, 문자열, 브루트포스, 다이나믹 프로그래밍, 그래프 이론, DFS, BFS, 백트래킹, 분할정복,
            이분탐색, 정렬, 자료구조, 트리, 수학, 정수론, 조합론 등 다양한 알고리즘 유형을 체계적으로 관리합니다.
            각 유형별로 초급, 중급, 고급, 마스터 레벨로 분류하여 단계적 학습을 지원합니다.
          </p>
        </section>
      </header>

      <SidebarProvider defaultOpen={false}>
        <LandingAppSidebar />
        <SidebarInset>
          <LandingPageContent />
        </SidebarInset>
        {/* 온보딩 컨트롤러 */}
        {isActive && <OnboardingController />}
      </SidebarProvider>
    </>
  );
}
