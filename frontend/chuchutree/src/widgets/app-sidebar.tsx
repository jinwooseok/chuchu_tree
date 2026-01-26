'use client';

import { Calendar, ChevronUp, Dices, Gem, Leaf, LibraryBig, PanelLeft, User2, Settings, LogOut, BookX, BookOpen, RefreshCw, PackageOpen } from 'lucide-react';
import { useLayoutStore } from '@/lib/store/layout';
import { useUser } from '@/entities/user/model/queries';
import { useRouter } from 'next/navigation';
import { useRefreshButtonStore } from '@/lib/store/refreshButton';
import { useRefresh } from '@/entities/refresh';

import { Sidebar, SidebarContent, SidebarFooter, SidebarGroup, SidebarGroupAction, SidebarGroupContent, SidebarMenu, SidebarMenuButton, SidebarMenuItem } from '@/components/ui/sidebar';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '@/components/ui/dropdown-menu';
import { useSidebar } from '@/components/ui/sidebar';
import Image from 'next/image';
import { AddPrevProblemsDialog, BannedProblemsDialog, SettingsDialog } from '@/features/sidebar';
import { TargetCode } from '@/shared/constants/tagSystem';
import { useModal } from '@/lib/providers/modal-provider';
import { toast } from '@/lib/utils/toast';
import { useLogout } from '@/entities/auth';
import { AppTooltip } from '@/components/custom/tooltip/AppTooltip';
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip';
import { Spinner } from '@/shared/ui';
import { useGlobalShortcuts } from '@/lib/hooks/useGlobalShortcuts';

const ICON_SIZE = 32;

export function AppSidebar() {
  const { state: sidebarOpenState, toggleSidebar: setSidebarOpenState } = useSidebar();
  const { topSection, centerSection, bottomSection, toggleTopSection, setCenterSection, toggleBottomSection } = useLayoutStore();
  const { data: user } = useUser();
  const { openModal, closeModal } = useModal();
  const router = useRouter();
  const { isRefreshButtonVisible, showRefreshButton } = useRefreshButtonStore();
  const { mutate: refresh, isPending: isRefreshPending } = useRefresh({
    onSuccess: () => {
      toast.success('프로필이 갱신되었습니다.');
    },
    onError: () => {
      toast.error('프로필 갱신에 실패했습니다');
    },
  });

  // 로그아웃 훅 및 핸들러
  const { mutate: logout } = useLogout({
    onSuccess: () => {
      toast.success('로그아웃되었습니다.');
      router.push('/sign-in');
    },
    onError: () => {
      toast.error('로그아웃에 실패했습니다. 다시 시도해주세요.');
    },
  });

  const handleLogout = () => {
    logout();
  };

  // Menu items.
  const items = [
    {
      title: '티어',
      action: () => toggleTopSection('tierbar'),
      icon: Gem,
      isActive: topSection === 'tierbar',
      tooltipText: '내 티어',
    },
    {
      title: '스트릭',
      action: () => toggleTopSection('streak'),
      icon: Leaf,
      isActive: topSection === 'streak',
      tooltipText: '1년간 문제 풀이 기록',
    },
    {
      title: '캘린더',
      action: () => setCenterSection('calendar'),
      icon: Calendar,
      isActive: centerSection === 'calendar',
      tooltipText: '문제 풀이 일정 관리',
    },
    {
      title: '유형별 숙련도',
      action: () => setCenterSection('dashboard'),
      icon: LibraryBig,
      isActive: centerSection === 'dashboard',
      tooltipText: '유형별 실력 현황',
    },
    {
      title: '오늘의 문제',
      action: () => toggleBottomSection(),
      icon: Dices,
      isActive: bottomSection === 'recommend',
      tooltipText: '사용자 맞춤 문제 추천',
    },
  ];

  return (
    <>
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
                  <Image src="/logo/logo.svg" alt="logo" width={24} height={32} />
                </div>
                <h1 className={`text-md ml-9 font-bold ${sidebarOpenState !== 'collapsed' ? 'max-h-8 opacity-100' : 'max-h-0 opacity-0'}`}>ChuChuTree</h1>
              </div>
              {/* 사이드 바 토글 (header) */}
              <AppTooltip content="사이드바 닫기" side="right">
                <SidebarGroupAction aria-label="사이드바 닫기">
                  <PanelLeft onClick={setSidebarOpenState} size={ICON_SIZE} className={`cursor-pointer`} /> <span className="sr-only">Toggle Sidebar OpenState</span>
                </SidebarGroupAction>
              </AppTooltip>
            </header>
            {/* link list */}
            <SidebarGroupContent>
              <SidebarMenu>
                {/* 사이드바 토글버튼 (inside) */}
                <div className={`transition-all duration-200 ease-in-out ${sidebarOpenState === 'collapsed' ? 'max-h-8 opacity-100' : 'max-h-0 opacity-0'}`}>
                  <SidebarMenuItem key="toggleSidebarOpenState">
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <SidebarMenuButton asChild>
                          <PanelLeft onClick={setSidebarOpenState} size={ICON_SIZE} className="cursor-pointer" />
                        </SidebarMenuButton>
                      </TooltipTrigger>
                      <TooltipContent side="right">사이드바 열기</TooltipContent>
                    </Tooltip>
                  </SidebarMenuItem>
                </div>
                {/* 나머지 link */}
                {items.map((item) => (
                  <SidebarMenuItem key={item.title} aria-label={item.tooltipText}>
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <SidebarMenuButton asChild isActive={item.isActive}>
                          <div onClick={item.action} className="cursor-pointer">
                            <item.icon size={ICON_SIZE} />
                            <span>{item.title}</span>
                          </div>
                        </SidebarMenuButton>
                      </TooltipTrigger>
                      <TooltipContent side="right">{item.tooltipText}</TooltipContent>
                    </Tooltip>
                  </SidebarMenuItem>
                ))}
              </SidebarMenu>
            </SidebarGroupContent>
          </SidebarGroup>
          <div className="mt-10" />
          {/* 그룹2 */}
          <SidebarGroup>
            <SidebarGroupContent>
              <SidebarMenu>
                <SidebarMenuItem key="addPrevProblems" aria-label={'가입일 이전 문제 등록하기'}>
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <SidebarMenuButton asChild>
                        <div
                          onClick={() => {
                            openModal('add-prev-problems', <AddPrevProblemsDialog onClose={() => closeModal('add-prev-problems')} />);
                          }}
                          className="cursor-pointer"
                        >
                          <BookOpen size={ICON_SIZE} />
                          <span>가입 전 풀이 등록하기</span>
                        </div>
                      </SidebarMenuButton>
                    </TooltipTrigger>
                    <TooltipContent side="right">가입일 이전 문제 등록하기</TooltipContent>
                  </Tooltip>
                </SidebarMenuItem>
                <SidebarMenuItem key="bannedProblemsList" aria-label={'bannedProblemsList'}>
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <SidebarMenuButton asChild>
                        <div
                          onClick={() => {
                            openModal('banned-problems-list', <BannedProblemsDialog onClose={() => closeModal('banned-problems-list')} />);
                          }}
                          className="cursor-pointer"
                        >
                          <BookX size={ICON_SIZE} />
                          <span>제외된 문제 확인하기</span>
                        </div>
                      </SidebarMenuButton>
                    </TooltipTrigger>
                    <TooltipContent side="right">제외된 문제 확인하기</TooltipContent>
                  </Tooltip>
                </SidebarMenuItem>
                <SidebarMenuItem key="refresh" aria-label={'프로필 갱신'}>
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <SidebarMenuButton asChild>
                        <div onClick={() => refresh()} className="cursor-pointer">
                          {isRefreshPending ? <Spinner /> : <RefreshCw className="text-foreground h-5 w-5" />}
                          <span>프로필 갱신</span>
                        </div>
                      </SidebarMenuButton>
                    </TooltipTrigger>
                    <TooltipContent side="right">프로필 갱신</TooltipContent>
                  </Tooltip>
                </SidebarMenuItem>
                {!isRefreshButtonVisible && (
                  <SidebarMenuItem key="showRefreshButton" aria-label={'버튼 꺼내기'}>
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <SidebarMenuButton asChild>
                          <div onClick={() => showRefreshButton()} className="cursor-pointer">
                            <PackageOpen size={ICON_SIZE} />
                            <span>버튼 꺼내기</span>
                          </div>
                        </SidebarMenuButton>
                      </TooltipTrigger>
                      <TooltipContent side="right">RefreshButton 꺼내기</TooltipContent>
                    </Tooltip>
                  </SidebarMenuItem>
                )}
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
                  <DropdownMenuItem
                    onSelect={(e) => {
                      e.preventDefault();
                      openModal(
                        'settings',
                        <SettingsDialog
                          currentBjAccountId={user?.bjAccount?.bjAccountId || ''}
                          currentTarget={user?.userAccount?.target?.targetCode as TargetCode}
                          linkedAt={user?.linkedAt}
                          onClose={() => closeModal('settings')}
                        />,
                      );
                    }}
                  >
                    <Settings className="mr-2 h-4 w-4" />
                    <span>설정</span>
                  </DropdownMenuItem>
                  <DropdownMenuItem
                    onSelect={(e) => {
                      e.preventDefault();
                      handleLogout();
                    }}
                  >
                    <LogOut className="mr-2 h-4 w-4" />
                    <span>로그아웃</span>
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </SidebarMenuItem>
          </SidebarMenu>
        </SidebarFooter>
      </Sidebar>
    </>
  );
}
