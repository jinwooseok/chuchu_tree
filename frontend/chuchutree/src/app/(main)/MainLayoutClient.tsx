'use client';

import { AppSidebar } from '@/widgets/app-sidebar';
import { SidebarInset, SidebarProvider } from '@/components/ui/sidebar';
import { useSetUser } from '@/lib/store/user';
import { User } from '@/entities/user';
import { useEffect } from 'react';

interface MainLayoutClientProps {
  children: React.ReactNode;
  initialUserData: User;
}

export function MainLayoutClient({ children, initialUserData }: MainLayoutClientProps) {
  const setUser = useSetUser();

  // 서버에서 받은 User 데이터를 Zustand store에 저장
  useEffect(() => {
    if (initialUserData) {
      setUser(initialUserData);
    }
  }, [initialUserData, setUser]);

  return (
    <SidebarProvider defaultOpen={false}>
      <AppSidebar />
      <SidebarInset>{children}</SidebarInset>
    </SidebarProvider>
  );
}
