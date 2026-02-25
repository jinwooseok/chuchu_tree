'use client';

import {
  Calendar,
  ChevronUp,
  Dices,
  Gem,
  Leaf,
  LibraryBig,
  PanelLeft,
  User2,
  Settings,
  LogOut,
  BookX,
  BookOpen,
  RefreshCw,
  PackageOpen,
  House,
  Lightbulb,
  SquarePlay,
  Loader,
  Bell,
  Star,
  Bookmark,
  CircleFadingPlus,
} from 'lucide-react';
import { useLayoutStore } from '@/lib/store/layout';
import { useRouter } from 'next/navigation';
import Image from 'next/image';
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupAction,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarMenuSub,
  SidebarMenuSubButton,
  SidebarMenuSubItem,
  SidebarRail,
} from '@/components/ui/sidebar';
import { useSidebar } from '@/components/ui/sidebar';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '@/components/ui/dropdown-menu';
import { TargetCode } from '@/shared/constants/tagSystem';
import { useLogout } from '@/entities/auth';
import { useModal } from '@/lib/providers/modal-provider';
import { toast } from '@/lib/utils/toast';
import { AppTooltip } from '@/components/custom/tooltip/AppTooltip';
import { useGlobalShortcuts } from '@/lib/hooks/useGlobalShortcuts';
import { useRefresh } from '@/entities/refresh';
import { useRefreshButtonStore } from '@/lib/store/refreshButton';
import { useRecommend } from '@/features/recommendation/hooks/useRecommend';
import { SettingsDialog } from '@/features/sidebar/ui/settings/SettingsDialog';
import { AddPrevProblemsDialog } from '@/features/sidebar/ui/group-second/AddPrevProblemsDialog';
import { BannedProblemsDialog } from '@/features/sidebar/ui/group-second/BannedProblemsDialog';
import { User } from '@/entities/user';
import { useState } from 'react';
import { useLandingRecommend } from '@/features/landing';
import { useOnboardingStore } from '@/lib/store/onboarding';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible';
import { CreateStudyDialog } from '@/features/sidebar/ui/group-study/CreateStudyDialog';
import { NoticeDialog } from '@/features/sidebar/ui/group-notification/NoticeDialog';
import { useNotificationStore } from '@/lib/store/notification';

const ICON_SIZE = 32;

export function AppSidebarInset({ user, isLanding = false }: { user?: User; isLanding?: boolean }) {
  const { openModal, closeModal } = useModal();
  const router = useRouter();
  // 사이드바 상태
  const { state: sidebarOpenState, toggleSidebar: setSidebarOpenState } = useSidebar();
  // 레이아웃 상태
  const { topSection, centerSection, bottomSection, toggleTopSection, setCenterSection, toggleBottomSection } = useLayoutStore();

  // 알림 dot 상태
  const { hasUnread } = useNotificationStore();

  // 리프래시버튼 훅
  const { isRefreshButtonVisible, showRefreshButton } = useRefreshButtonStore();
  const { mutate: refresh, isPending: isRefreshPending } = useRefresh({
    onSuccess: () => {
      toast.success('프로필이 갱신되었습니다.');
    },
    onError: () => {
      toast.error('프로필 갱신에 실패했습니다');
    },
  });
  const [isLendingRefreshPending, setIsLandingRefreshPending] = useState<boolean>(false);
  const isPending = isRefreshPending || isLendingRefreshPending;
  // 리프래시버튼 클릭시 2초 대기 후 성공
  const landingRefresh = () => {
    setIsLandingRefreshPending(true);

    setTimeout(() => {
      setIsLandingRefreshPending(false);
      toast.success('프로필이 갱신되었습니다.');
    }, 2000);
  };
  // 리프래시버튼 핸들러
  const handleRefresh = () => {
    if (isLanding) {
      landingRefresh();
    } else {
      refresh();
    }
  };

  // 로그아웃 훅
  const { mutate: logout } = useLogout({
    onSuccess: () => {
      toast.success('로그아웃되었습니다.');
      router.push('/sign-in');
    },
    onError: () => {
      toast.error('로그아웃에 실패했습니다. 다시 시도해주세요.');
    },
  });

  // 로그아웃 핸들러
  const handleLogout = () => {
    if (isLanding) {
      router.push('/chu');
    } else {
      logout();
    }
  };

  // 추천받기 훅 + 핸들러
  const { recommend } = useRecommend();
  const { recommend: landingRecommend } = useLandingRecommend();
  const handleRecommend = () => {
    if (isLanding) {
      landingRecommend();
    } else {
      recommend();
    }
  };

  // 가입전문제 모달 열기
  const handleAddPrevProblems = () => {
    openModal('add-prev-problems', <AddPrevProblemsDialog user={user} isLanding={isLanding} onClose={() => closeModal('add-prev-problems')} />);
  };
  // 제외된 문제 모달 열기
  const handleBannedList = () => {
    if (isLanding) {
      toast.info('로그인 후 이용가능합니다.');
      return;
    }
    openModal('banned-problems-list', <BannedProblemsDialog onClose={() => closeModal('banned-problems-list')} />);
  };

  // 설정 모달 열기
  const handleOpenSettings = () => {
    openModal(
      'settings',
      <SettingsDialog
        currentBjAccountId={user?.bjAccount?.bjAccountId || 'guest'}
        currentTarget={user?.userAccount?.target?.targetCode as TargetCode}
        linkedAt={user?.linkedAt}
        isLanding={isLanding}
        onClose={() => closeModal('settings')}
      />,
    );
  };

  // 스터디 생성 모달 열기
  const handleCreateStudy = () => {
    if (isLanding) {
      toast.info('로그인 후 이용가능합니다.');
      return;
    }
    openModal('create-study', <CreateStudyDialog user={user} onClose={() => closeModal('create-study')} />);
  };
  // 알림 모달 열기
  const handleNotice = () => {
    if (isLanding) {
      toast.info('로그인 후 이용가능합니다.');
      return;
    }
    openModal('notice-list', <NoticeDialog onClose={() => closeModal('notice-list')} />);
  };

  // 튜토리얼 다시보기
  const { resetOnboarding, startOnboarding } = useOnboardingStore();
  const handleTutorialStart = () => {
    resetOnboarding(); // localStorage에서 완료 플래그 제거
    startOnboarding(); // 온보딩 시작
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
          handleRecommend();
        },
        description: '추천받기',
      },
      // Shift + R: 프로필 갱신
      {
        key: 'r',
        shift: true,
        action: () => {
          if (!isPending) {
            handleRefresh();
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
      onboardingId: 'tierbar-button',
    },
    {
      title: '스트릭',
      short1: 'Shift',
      short2: '2',
      action: () => toggleTopSection('streak'),
      icon: Leaf,
      isActive: topSection === 'streak',
      tooltipText: '1년간 문제 풀이 기록',
      onboardingId: 'streakbar-button',
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
      onboardingId: 'dashboard-button',
    },
    {
      title: '오늘의 문제',
      short1: 'Shift',
      short2: '3',
      action: () => toggleBottomSection(),
      icon: Dices,
      isActive: bottomSection === 'recommend',
      tooltipText: '사용자 맞춤 문제 추천',
      onboardingId: 'recommend-button',
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
                <div className={`text-md ml-9 flex flex-col font-bold ${sidebarOpenState !== 'collapsed' ? 'max-h-8 opacity-100' : 'max-h-0 opacity-0'}`}>
                  <span>ChuChuTree</span>
                  {isLanding ? (
                    <span className="bg-primary rounded-sm px-2 text-end text-sm font-medium text-white">튜토리얼</span>
                  ) : (
                    <span className="text-muted-foreground text-end text-sm font-medium">ver1.0</span>
                  )}
                </div>
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
                        <div onClick={item.action} className="cursor-pointer" {...(item.onboardingId ? { 'data-onboarding-id': item.onboardingId } : {})}>
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
                  <AppTooltip content={user?.userAccount?.isSynced === false ? '첫 가입 후 꼭 해주세요!' : '가입일 이전 문제 등록하기'} side="right">
                    <SidebarMenuButton asChild>
                      <div
                        onClick={handleAddPrevProblems}
                        className={`relative cursor-pointer ${user?.userAccount?.isSynced === false ? 'border-primary border-2' : ''}`}
                        data-onboarding-id="add-prev-problems-button"
                      >
                        {user?.userAccount?.isSynced === false && (
                          <div className="pointer-events-none absolute inset-0 overflow-hidden">
                            <div className="star-border-active" />
                          </div>
                        )}
                        <BookOpen size={ICON_SIZE} className="relative z-10" />
                        <span className="relative z-10">가입 전 풀이 등록하기</span>
                      </div>
                    </SidebarMenuButton>
                  </AppTooltip>
                </SidebarMenuItem>
                <SidebarMenuItem key="bannedProblemsList" aria-label={'bannedProblemsList'}>
                  <AppTooltip content="제외된 문제 확인하기" side="right">
                    <SidebarMenuButton asChild>
                      <div onClick={handleBannedList} className="cursor-pointer">
                        <BookX size={ICON_SIZE} />
                        <span>제외된 문제 확인하기</span>
                      </div>
                    </SidebarMenuButton>
                  </AppTooltip>
                </SidebarMenuItem>
                <SidebarMenuItem key="refresh" aria-label={'프로필 갱신'}>
                  <AppTooltip content="프로필 갱신" side="right" shortCut1="Shift" shortCut2="R">
                    <SidebarMenuButton asChild>
                      <div onClick={handleRefresh} className="cursor-pointer" data-onboarding-id="refresh-button">
                        {isPending ? <Loader className="text-foreground h-5 w-5 animate-spin" style={{ animationDuration: '2s' }} /> : <RefreshCw className="text-foreground h-5 w-5" />}
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
          <div className="mt-10" />
          {/* 그룹3 : 스터디 전용 */}
          <SidebarGroup>
            <SidebarGroupContent>
              <SidebarMenu>
                <SidebarMenuItem key="addstudy" aria-label={'스터디 생성'}>
                  <AppTooltip content={'스터디 생성'} side="right">
                    <SidebarMenuButton asChild>
                      <div onClick={handleCreateStudy} className="cursor-pointer">
                        <CircleFadingPlus size={ICON_SIZE} className="relative z-10" />
                        <span className="relative z-10">스터디 만들기</span>
                      </div>
                    </SidebarMenuButton>
                  </AppTooltip>
                </SidebarMenuItem>
                <SidebarMenuItem key="studygroup" aria-label={'스터디'}>
                  <AppTooltip content={'스터디를 만들어보세요'} side="right">
                    <SidebarMenuButton asChild>
                      <div onClick={() => {}} className="cursor-pointer">
                        <Star size={ICON_SIZE} className="relative z-10" />
                        <span className="relative z-10">스터디 목록</span>
                      </div>
                    </SidebarMenuButton>
                  </AppTooltip>
                  <SidebarMenuSub>
                    <SidebarMenuSubItem>
                      <SidebarMenuSubButton asChild>
                        <div onClick={() => {}} className="cursor-pointer">
                          <Bookmark size={ICON_SIZE} className="relative z-10" />
                          <span className="relative z-10">스터디1</span>
                        </div>
                      </SidebarMenuSubButton>
                      <SidebarMenuSubButton asChild>
                        <div onClick={() => {}} className="cursor-pointer">
                          <Bookmark size={ICON_SIZE} className="relative z-10" />
                          <span className="relative z-10">스터디2</span>
                        </div>
                      </SidebarMenuSubButton>
                      <SidebarMenuSubButton asChild>
                        <div onClick={() => {}} className="cursor-pointer">
                          <Bookmark size={ICON_SIZE} className="relative z-10" />
                          <span className="relative z-10">스터디3</span>
                        </div>
                      </SidebarMenuSubButton>
                    </SidebarMenuSubItem>
                  </SidebarMenuSub>
                </SidebarMenuItem>
              </SidebarMenu>
            </SidebarGroupContent>
          </SidebarGroup>
        </SidebarContent>
        {/* footer */}
        <SidebarFooter>
          <SidebarGroupContent>
            <SidebarMenu>
              {/* 랜딩 전용 입장하기 */}
              {isLanding && (
                <>
                  <SidebarMenuItem key="start-onboarding" aria-label={'튜토리얼 다시보기'}>
                    <AppTooltip content="튜토리얼 다시보기" side="right">
                      <SidebarMenuButton asChild>
                        <div onClick={handleTutorialStart} className="cursor-pointer">
                          <SquarePlay size={ICON_SIZE} />
                          <span>튜토리얼 다시보기</span>
                        </div>
                      </SidebarMenuButton>
                    </AppTooltip>
                  </SidebarMenuItem>
                  <SidebarMenuItem key="enter-main-page" aria-label={'입장하기'}>
                    <AppTooltip content="로그인 하러가기" side="right">
                      <SidebarMenuButton asChild>
                        <div
                          onClick={() => {
                            router.push('/chu');
                          }}
                          className="cursor-pointer"
                        >
                          <House size={ICON_SIZE} />
                          <span>로그인</span>
                        </div>
                      </SidebarMenuButton>
                    </AppTooltip>
                  </SidebarMenuItem>
                </>
              )}
              {/* 실 서비스 전용 튜토리얼 이동하기*/}
              {!isLanding && (
                <SidebarMenuItem key="bell" aria-label={'알림 및 업데이트 알림'}>
                  <AppTooltip content="알림 및 업데이트 알림" side="right">
                    <SidebarMenuButton asChild>
                      <div onClick={handleNotice} className="cursor-pointer">
                        <div className="relative h-4 w-4">
                          <Bell className="h-4 w-4" />
                          {hasUnread && <div className="bg-primary absolute -top-0.5 -right-0.5 h-2 w-2 rounded-full" />}
                        </div>
                        <span>알림</span>
                      </div>
                    </SidebarMenuButton>
                  </AppTooltip>
                </SidebarMenuItem>
              )}
            </SidebarMenu>
          </SidebarGroupContent>
          {/* 드롭다운 */}
          <SidebarMenu>
            <SidebarMenuItem>
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <SidebarMenuButton>
                    <User2 /> {user?.bjAccount.bjAccountId ?? 'Guest'}
                    <ChevronUp className="ml-auto" />
                  </SidebarMenuButton>
                </DropdownMenuTrigger>
                <DropdownMenuContent side="top" className="w-[radix-popper-anchor-width]">
                  <AppTooltip content="설정" side="right" shortCut1="Ctrl" shortCut2="`">
                    <DropdownMenuItem
                      onSelect={(e) => {
                        e.preventDefault();
                        handleOpenSettings();
                      }}
                    >
                      <Settings className="mr-2 h-4 w-4" />
                      <span>설정</span>
                    </DropdownMenuItem>
                  </AppTooltip>
                  {!isLanding && (
                    <AppTooltip content="튜토리얼 이동하기" side="right">
                      <DropdownMenuItem
                        onSelect={(e) => {
                          handleTutorialStart();
                        }}
                      >
                        <Lightbulb className="mr-2 h-4 w-4" />
                        <span>튜토리얼</span>
                      </DropdownMenuItem>
                    </AppTooltip>
                  )}
                  <DropdownMenuItem
                    onSelect={(e) => {
                      e.preventDefault();
                      handleLogout();
                    }}
                  >
                    <LogOut className="mr-2 h-4 w-4" />
                    <span>{isLanding ? '입장하기' : '로그아웃'}</span>
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
