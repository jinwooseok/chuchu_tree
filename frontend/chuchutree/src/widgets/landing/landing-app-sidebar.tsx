'use client';

import { Calendar, ChevronUp, Dices, Gem, Leaf, LibraryBig, PanelLeft, User2, Settings, LogOut, BookX, BookOpen, RefreshCw, PackageOpen } from 'lucide-react';
import { useLayoutStore } from '@/lib/store/layout';
import { useRouter } from 'next/navigation';
import { useRefreshButtonStore } from '@/lib/store/refreshButton';
import { Sidebar, SidebarContent, SidebarFooter, SidebarGroup, SidebarGroupAction, SidebarGroupContent, SidebarMenu, SidebarMenuButton, SidebarMenuItem } from '@/components/ui/sidebar';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '@/components/ui/dropdown-menu';
import { useSidebar } from '@/components/ui/sidebar';
import Image from 'next/image';
import { AddPrevProblemsDialog, BannedProblemsDialog, SettingsDialog } from '@/features/sidebar';
import { TargetCode } from '@/shared/constants/tagSystem';
import { useModal } from '@/lib/providers/modal-provider';
import { toast } from '@/lib/utils/toast';
import { AppTooltip } from '@/components/custom/tooltip/AppTooltip';
import { Spinner } from '@/shared/ui';
import { useGlobalShortcuts } from '@/lib/hooks/useGlobalShortcuts';
import { useLandingRecommend } from '@/features/landing/hooks/useLandingRecommend';
import { useState } from 'react';

const ICON_SIZE = 32;

export function LandingAppSidebar() {
  const { state: sidebarOpenState, toggleSidebar: setSidebarOpenState } = useSidebar();
  const { topSection, centerSection, bottomSection, toggleTopSection, setCenterSection, toggleBottomSection } = useLayoutStore();
  const { openModal, closeModal } = useModal();
  const router = useRouter();
  const { isRefreshButtonVisible, showRefreshButton } = useRefreshButtonStore();

  const [isRefreshPending, setIsRefreshPending] = useState<boolean>(false);
  // 리프래시버튼 클릭시 2초 대기 후 성공
  const refresh = () => {
    setIsRefreshPending(true);

    setTimeout(() => {
      setIsRefreshPending(false);
      toast.success('프로필이 갱신되었습니다.');
    }, 2000);
  };

  // 로그아웃 훅 및 핸들러
  // => 로그인페이지로 이동

  // 추천받기 훅 (랜딩페이지용)
  const { recommend } = useLandingRecommend();

  // 설정 모달 열기
  const handleOpenSettings = () => {
    openModal('settings', <SettingsDialog currentBjAccountId={'Guest'} currentTarget={'CT' as TargetCode} linkedAt={'2027-01-13T13:52:25'} onClose={() => closeModal('settings')} />);
  };

  // 전역 단축키 등록
  useGlobalShortcuts({
    shortcuts: [
      // Shift + C: 캘린더 뷰로 전환
      {
        key: 'c',
        shift: true,
        action: () => setCenterSection('calendar'),
        description: '캘린더 뷰로 전환',
      },
      // Shift + D: 대시보드 뷰로 전환
      {
        key: 'd',
        shift: true,
        action: () => setCenterSection('dashboard'),
        description: '대시보드 뷰로 전환',
      },
      // Shift + 1: 티어바 토글
      {
        key: '1',
        code: 'Digit1',
        shift: true,
        action: () => toggleTopSection('tierbar'),
        description: '티어바 토글',
      },
      // Shift + 2: 스트릭바 토글
      {
        key: '2',
        code: 'Digit2',
        shift: true,
        action: () => toggleTopSection('streak'),
        description: '스트릭바 토글',
      },
      // Shift + 3: 추천 섹션 토글
      {
        key: '3',
        code: 'Digit3',
        shift: true,
        action: () => toggleBottomSection(),
        description: '추천 섹션 토글',
      },
      // Shift + E: 추천받기
      {
        key: 'e',
        shift: true,
        action: () => {
          // 추천 섹션이 닫혀있으면 먼저 열기
          if (bottomSection !== 'recommend') {
            toggleBottomSection();
          }
          // store 상태를 사용하여 추천받기 실행
          recommend();
        },
        description: '추천받기',
      },
      // Shift + R: 프로필 갱신
      {
        key: 'r',
        shift: true,
        action: () => {
          if (!isRefreshPending) {
            refresh();
          }
        },
        description: '프로필 갱신',
      },
      // Ctrl + `: 설정 열기
      {
        key: '`',
        code: 'Backquote',
        ctrl: true,
        action: handleOpenSettings,
        description: '설정 열기',
      },
    ],
  });

  // Menu items.
  const items = [
    {
      title: '티어',
      short1: 'Shift',
      short2: '1',
      action: () => toggleTopSection('tierbar'),
      icon: Gem,
      isActive: topSection === 'tierbar',
      tooltipText: '내 티어',
    },
    {
      title: '스트릭',
      short1: 'Shift',
      short2: '2',
      action: () => toggleTopSection('streak'),
      icon: Leaf,
      isActive: topSection === 'streak',
      tooltipText: '1년간 문제 풀이 기록',
    },
    {
      title: '캘린더',
      short1: 'Shift',
      short2: 'C',
      action: () => setCenterSection('calendar'),
      icon: Calendar,
      isActive: centerSection === 'calendar',
      tooltipText: '문제 풀이 일정 관리',
    },
    {
      title: '유형별 숙련도',
      short1: 'Shift',
      short2: 'D',
      action: () => setCenterSection('dashboard'),
      icon: LibraryBig,
      isActive: centerSection === 'dashboard',
      tooltipText: '유형별 실력 현황',
    },
    {
      title: '오늘의 문제',
      short1: 'Shift',
      short2: '3',
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
              <AppTooltip content="사이드바 닫기" side="right" shortCut1="Shift" shortCut2="B">
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
                    <AppTooltip content="사이드바 닫기" side="right" shortCut1="Shift" shortCut2="B">
                      <SidebarMenuButton asChild>
                        <PanelLeft onClick={setSidebarOpenState} size={ICON_SIZE} className="cursor-pointer" />
                      </SidebarMenuButton>
                    </AppTooltip>
                  </SidebarMenuItem>
                </div>
                {/* 나머지 link */}
                {items.map((item) => (
                  <SidebarMenuItem key={item.title} aria-label={item.tooltipText}>
                    <AppTooltip content={item.tooltipText} side="right" shortCut1={item.short1} shortCut2={item.short2}>
                      <SidebarMenuButton asChild isActive={item.isActive}>
                        <div onClick={item.action} className="cursor-pointer">
                          <item.icon size={ICON_SIZE} />
                          <span>{item.title}</span>
                        </div>
                      </SidebarMenuButton>
                    </AppTooltip>
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
                  <AppTooltip content="가입일 이전 문제 등록하기" side="right">
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
                  </AppTooltip>
                </SidebarMenuItem>
                <SidebarMenuItem key="bannedProblemsList" aria-label={'bannedProblemsList'}>
                  <AppTooltip content="제외된 문제 확인하기" side="right">
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
                  </AppTooltip>
                </SidebarMenuItem>
                <SidebarMenuItem key="refresh" aria-label={'프로필 갱신'}>
                  <AppTooltip content="프로필 갱신" side="right" shortCut1="Shift" shortCut2="R">
                    <SidebarMenuButton asChild>
                      <div onClick={() => refresh()} className="cursor-pointer">
                        {isRefreshPending ? <Spinner /> : <RefreshCw className="text-foreground h-5 w-5" />}
                        <span>프로필 갱신</span>
                      </div>
                    </SidebarMenuButton>
                  </AppTooltip>
                </SidebarMenuItem>
                {!isRefreshButtonVisible && (
                  <SidebarMenuItem key="showRefreshButton" aria-label={'버튼 꺼내기'}>
                    <AppTooltip content="프로필 갱신 버튼 꺼내기" side="right">
                      <SidebarMenuButton asChild>
                        <div onClick={() => showRefreshButton()} className="cursor-pointer">
                          <PackageOpen size={ICON_SIZE} />
                          <span>버튼 꺼내기</span>
                        </div>
                      </SidebarMenuButton>
                    </AppTooltip>
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
                    <User2 /> {'Guest'}
                    <ChevronUp className="ml-auto" />
                  </SidebarMenuButton>
                </DropdownMenuTrigger>
                <DropdownMenuContent side="top" className="w-[radix-popper-anchor-width]">
                  <AppTooltip content="설정" side="right" shortCut1="Ctrl" shortCut2="`">
                    <DropdownMenuItem
                      onSelect={(e) => {
                        e.preventDefault();
                        openModal(
                          'settings',
                          <SettingsDialog currentBjAccountId={'Guest'} currentTarget={'CT' as TargetCode} linkedAt={'2027-01-13T13:52:25'} onClose={() => closeModal('settings')} />,
                        );
                      }}
                    >
                      <Settings className="mr-2 h-4 w-4" />
                      <span>설정</span>
                    </DropdownMenuItem>
                  </AppTooltip>
                  <DropdownMenuItem
                    onSelect={(e) => {
                      e.preventDefault();
                      router.push('/sign-in');
                    }}
                  >
                    <LogOut className="mr-2 h-4 w-4" />
                    <span>로그인</span>
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
