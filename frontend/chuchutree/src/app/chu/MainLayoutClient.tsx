'use client';

import { AppSidebar } from '@/widgets/app-sidebar';
import { SidebarInset, SidebarProvider } from '@/components/ui/sidebar';
import { useOnboardingStore } from '@/lib/store/onboarding';
import { OnboardingController } from '@/features/landing';

interface MainLayoutClientProps {
  children: React.ReactNode;
}

export function MainLayoutClient({ children }: MainLayoutClientProps) {

const { hasCompletedOnboarding, isActive, _hasHydrated, startOnboarding } = useOnboardingStore();

  // SSR prefetch 데이터는 HydrationBoundary가 자동으로 Query cache에 주입
  // Zustand 동기화 로직 제거 - 컴포넌트가 직접 Query hooks 사용

  return (
    <SidebarProvider defaultOpen={false}>
      <AppSidebar />
      <SidebarInset>{children}</SidebarInset>
            {/* 온보딩 컨트롤러 */}
            {isActive && <OnboardingController />}
    </SidebarProvider>
  );
}
