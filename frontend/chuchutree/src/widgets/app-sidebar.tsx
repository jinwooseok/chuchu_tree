'use client';

import { Calendar, ChevronUp, Dices, Gem, Leaf, LibraryBig, PanelLeft, User2 } from 'lucide-react';
import { useLayoutStore } from '@/lib/store/layout';
import { useUser } from '@/lib/store/user';
import { useRouter } from 'next/navigation';

import { Sidebar, SidebarContent, SidebarFooter, SidebarGroup, SidebarGroupAction, SidebarGroupContent, SidebarMenu, SidebarMenuButton, SidebarMenuItem } from '@/components/ui/sidebar';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '@/components/ui/dropdown-menu';
import { useSidebar } from '@/components/ui/sidebar';
import Image from 'next/image';
import { ThemeButton } from '@/shared/ui';
import { TargetChangeDialog } from '@/features/target-change';
import { BjAccountChangeDialog } from '@/features/bj-account-change';
import { TargetCode } from '@/shared/constants/tagSystem';
import { useModal } from '@/lib/providers/modal-provider';
import { toast } from 'sonner';
import { useLogout } from '@/entities/auth';
import { AppTooltip } from '@/components/custom/tooltip/AppTooltip';
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip';

const ICON_SIZE = 32;

export function AppSidebar() {
  const { state: sidebarOpenState, toggleSidebar: setSidebarOpenState } = useSidebar();
  const { topSection, centerSection, bottomSection, toggleTopSection, setCenterSection, toggleBottomSection } = useLayoutStore();
  const { user } = useUser();
  const { openModal, closeModal } = useModal();
  const router = useRouter();

  // 7일 체크 함수
  const canChangeAccount = () => {
    if (!user?.linkedAt) return false;
    const linkedDate = new Date(user.linkedAt);
    const now = new Date();
    const diffInDays = Math.floor((now.getTime() - linkedDate.getTime()) / (1000 * 60 * 60 * 24));
    return diffInDays >= 7;
  };

  const handleAccountChange = () => {
    if (!canChangeAccount()) {
      const linkedDate = new Date(user?.linkedAt || '');
      const availableDate = new Date(linkedDate);
      availableDate.setDate(availableDate.getDate() + 7);
      const dateString = availableDate.toLocaleDateString().split('.').slice(1);
      const dateStringKr = `${dateString[0]}월${dateString[1]}일` || '';
      toast.error(`계정 재설정은 7일에 한 번만 가능합니다. ${dateStringKr} 이후에 다시 시도해주세요.`, {
        position: 'top-center',
      });
      return;
    }
    openModal('bj-account-change', <BjAccountChangeDialog currentBjAccountId={user?.bjAccount?.bjAccountId || ''} onClose={() => closeModal('bj-account-change')} />);
  };

  // 로그아웃 훅 및 핸들러
  const { mutate: logout, isPending: isLogoutPending } = useLogout({
    onSuccess: () => {
      toast.success('로그아웃되었습니다.', {
        position: 'top-center',
      });
      router.push('/sign-in');
    },
    onError: () => {
      toast.error('로그아웃에 실패했습니다. 다시 시도해주세요.', {
        position: 'top-center',
      });
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
                  <DropdownMenuItem
                    onSelect={(e) => {
                      e.preventDefault();
                      handleAccountChange();
                    }}
                  >
                    <span>연동 계정 재설정</span>
                  </DropdownMenuItem>
                  <DropdownMenuItem
                    onSelect={(e) => {
                      e.preventDefault();
                      openModal('target-change', <TargetChangeDialog currentTarget={user?.userAccount?.target?.targetCode as TargetCode} onClose={() => closeModal('target-change')} />);
                    }}
                  >
                    <span>목표 변경</span>
                  </DropdownMenuItem>
                  <DropdownMenuItem
                    onSelect={(e) => {
                      e.preventDefault();
                      handleLogout();
                    }}
                    disabled={isLogoutPending}
                  >
                    <span>{isLogoutPending ? '로그아웃 중...' : '로그아웃'}</span>
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
