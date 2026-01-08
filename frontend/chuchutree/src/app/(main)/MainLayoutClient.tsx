'use client';

import { AppSidebar } from '@/widgets/app-sidebar';
import { SidebarInset, SidebarProvider } from '@/components/ui/sidebar';
import { useSetUser } from '@/lib/store/user';
import { useSetCalendarData } from '@/lib/store/calendar';
import { User } from '@/entities/user';
import { Calendar } from '@/entities/calendar';
import { useEffect } from 'react';
import { TagDashboard } from '@/entities/tag-dashboard';
import { useSetTagDashboardData } from '@/lib/store/tagDashboard';

interface MainLayoutClientProps {
  children: React.ReactNode;
  initialUserData: User;
  initialCalendarData: Calendar | null;
  initialTagDashboard: TagDashboard | null;
}

export function MainLayoutClient({ children, initialUserData, initialCalendarData, initialTagDashboard }: MainLayoutClientProps) {
  const setUser = useSetUser();
  const setCalendarData = useSetCalendarData();
  const setTagDashboardData = useSetTagDashboardData();

  // 서버에서 받은 User 데이터를 Zustand store에 저장
  useEffect(() => {
    if (initialUserData) {
      setUser(initialUserData);
    }
  }, [initialUserData, setUser]);

  // 서버에서 받은 Calendar 데이터를 Zustand store에 저장
  useEffect(() => {
    if (initialCalendarData) {
      setCalendarData(initialCalendarData);
    }
  }, [initialCalendarData, setCalendarData]);

  // 서버에서 받은 TagDashboard 데이타 store 저장
  useEffect(() => {
    if (initialTagDashboard) {
      setTagDashboardData(initialTagDashboard);
    }
  }, [initialTagDashboard, setTagDashboardData]);

  return (
    <SidebarProvider defaultOpen={false}>
      <AppSidebar />
      <SidebarInset>{children}</SidebarInset>
    </SidebarProvider>
  );
}
