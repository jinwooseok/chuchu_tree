'use client';

import { Calendar, ChevronUp, Dices, Gem, Leaf, LibraryBig, PanelLeft, User2 } from 'lucide-react';
import { useLayoutStore } from '@/lib/store/layout';
import { useUser } from '@/lib/store/user';

import { Sidebar, SidebarContent, SidebarFooter, SidebarGroup, SidebarGroupAction, SidebarGroupContent, SidebarMenu, SidebarMenuButton, SidebarMenuItem } from '@/components/ui/sidebar';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '@/components/ui/dropdown-menu';
import { useSidebar } from '@/components/ui/sidebar';
import Image from 'next/image';
import { ThemeButton } from '@/shared/ui';

const ICON_SIZE = 32;

export function AppSidebar() {
  const { state: sidebarOpenState, toggleSidebar: setSidebarOpenState } = useSidebar();
  const { topSection, centerSection, bottomSection, toggleTopSection, setCenterSection, toggleBottomSection } = useLayoutStore();
  const { user } = useUser();

  // Menu items.
  const items = [
    {
      title: '티어',
      action: () => toggleTopSection('tierbar'),
      icon: Gem,
      isActive: topSection === 'tierbar',
    },
    {
      title: '스트릭',
      action: () => toggleTopSection('streak'),
      icon: Leaf,
      isActive: topSection === 'streak',
    },
    {
      title: '캘린더',
      action: () => setCenterSection('calendar'),
      icon: Calendar,
      isActive: centerSection === 'calendar',
    },
    {
      title: '유형별 숙련도',
      action: () => setCenterSection('dashboard'),
      icon: LibraryBig,
      isActive: centerSection === 'dashboard',
    },
    {
      title: '오늘의 문제',
      action: () => toggleBottomSection(),
      icon: Dices,
      isActive: bottomSection === 'recommend',
    },
  ];

  return (
    <Sidebar variant="inset" collapsible="icon">
      {/* 메인 콘텐츠 */}
      <SidebarContent className="relative">
        {/* 그룹1 */}
        <SidebarGroup>
          {/* 그룹1/헤더 */}
          <header className="">
            {/* 서비스아이콘 */}
            <div className="mt-1 mb-8 flex items-center">
              <div className="absolute top-2 left-3">
                <Image
                  src="/logo/logo.svg"
                  alt="logo"
                  width={ICON_SIZE} // 필수: 실제 로고 크기에 맞게 조정
                  height={ICON_SIZE} // 필수: 실제 로고 크기에 맞게 조정
                  className="h-8 w-6"
                />
              </div>
              <h1 className={`text-md ml-9 font-bold ${sidebarOpenState !== 'collapsed' ? 'max-h-8 opacity-100' : 'max-h-0 opacity-0'}`}>ChuChuTree</h1>
            </div>
            {/* 사이드 바 토글 (header) */}
            <SidebarGroupAction title="메뉴 접기">
              <PanelLeft onClick={setSidebarOpenState} size={ICON_SIZE} className={`cursor-pointer`} /> <span className="sr-only">Toggle Sidebar OpenState</span>
            </SidebarGroupAction>
          </header>
          {/* link list */}
          <SidebarGroupContent>
            <SidebarMenu>
              {/* 사이드바 토글버튼 (inside) */}
              <div className={`overflow-hidden transition-all duration-200 ease-in-out ${sidebarOpenState === 'collapsed' ? 'max-h-8 opacity-100' : 'max-h-0 opacity-0'}`}>
                <SidebarMenuItem key="toggleSidebarOpenState">
                  <SidebarMenuButton asChild>
                    <div>
                      <PanelLeft onClick={setSidebarOpenState} size={ICON_SIZE} className="cursor-pointer" /> <span className="sr-only">Toggle Sidebar OpenState in Sidebar</span>
                    </div>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              </div>
              {/* 나머지 link */}
              {items.map((item) => (
                <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton asChild isActive={item.isActive}>
                    <div onClick={item.action} className="cursor-pointer">
                      <item.icon size={ICON_SIZE} />
                      <span>{item.title}</span>
                    </div>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
      {/* footer */}
      <SidebarFooter>
        <SidebarMenu>
          <SidebarMenuItem>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <SidebarMenuButton>
                  <User2 /> {user?.bjAccount.bjAccountId ?? 'Guest'}
                  <ChevronUp className="ml-auto" />
                </SidebarMenuButton>
              </DropdownMenuTrigger>
              <DropdownMenuContent side="top" className="w-[--radix-popper-anchor-width]">
                <ThemeButton />
                <DropdownMenuItem>
                  <span>연동 계정 재설정</span>
                </DropdownMenuItem>
                <DropdownMenuItem>
                  <span>목표 변경</span>
                </DropdownMenuItem>
                <DropdownMenuItem>
                  <span>로그아웃</span>
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarFooter>
    </Sidebar>
  );
}
