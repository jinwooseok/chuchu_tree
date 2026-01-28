/**
 * 온보딩 플로우 데이터 정의
 */

export type SequenceType = 'f' | 'd' | 's' | 'u';

export interface OnboardingSequence {
  type: SequenceType;
  delay?: number; // 자동 진행 딜레이 (ms)
  duration?: number; // 애니메이션 지속 시간 (ms)

  // f, u 타입용 (포커싱)
  targetSelector?: string;
  message?: string | string[];
  tooltipPosition?: 'top' | 'bottom' | 'left' | 'right';
  buttonText?: string;
  highlightAnimation?: 'pulse' | 'arrow' | 'none';

  // d 타입용 (다이얼로그)
  dialogMessages?: string[];
  dialogButtons?: Array<{ text: string; action: 'next' | 'skip' | 'start' | 'login' }>;

  // s 타입용 (시스템 동작)
  systemAction?: () => void;

  // u 타입용 (사용자 인터랙션 대기)
  waitForEvent?: 'click' | 'custom';
  eventTarget?: string; // 클릭 대기할 요소의 selector
}

export interface OnboardingStep {
  stepNumber: number;
  title: string;
  sequences: OnboardingSequence[];
}

export const ONBOARDING_STEPS: OnboardingStep[] = [
  // Step 1: 환영 페이지
  {
    stepNumber: 1,
    title: '환영 페이지',
    sequences: [
      {
        type: 'd',
        dialogMessages: [
          'ChuChuTree에 오신 것을 환영합니다! 🎉',
          '알고리즘 문제 풀이를 체계적으로 관리하고 맞춤형 추천을 받을 수 있는 서비스입니다.',
          '지금부터 주요 기능들을 살펴보겠습니다.',
        ],
        dialogButtons: [{ text: '시작하기', action: 'start' }],
      },
      {
        type: 's',
        duration: 500,
        systemAction: () => {
          // 레이아웃 초기화는 OnboardingController에서 처리
          console.log('레이아웃 초기화');
        },
      },
      {
        type: 'd',
        dialogMessages: ['화면이 준비되었습니다. 캘린더 화면을 살펴볼까요?'],
        dialogButtons: [{ text: '다음', action: 'next' }],
      },
    ],
  },
  // Step 2: 캘린더 화면
  {
    stepNumber: 2,
    title: '캘린더 화면',
    sequences: [
      {
        type: 'd',
        dialogMessages: ['이곳은 캘린더 화면입니다.', '문제 풀이 일정을 한눈에 확인하고 관리할 수 있습니다.'],
        dialogButtons: [{ text: '다음', action: 'next' }],
      },
      {
        type: 'f',
        targetSelector: '[data-onboarding-id="big-calendar-today"]',
        message: ['캘린더에서 날짜를 선택하면,', '그날 풀었던 문제와 풀기로 한 문제가 표시됩니다.'],
        tooltipPosition: 'right',
        buttonText: '다음',
        duration: 300,
      },
      {
        type: 'f',
        targetSelector: '[data-onboarding-id="calendar-sidebar-solved"]',
        message: '여기서는 선택한 날짜에 해결한 문제 목록을 확인할 수 있습니다.',
        tooltipPosition: 'right',
        buttonText: '다음',
        duration: 300,
      },
      {
        type: 'f',
        targetSelector: '[data-onboarding-id="calendar-sidebar-scheduled"]',
        message: '풀기로 한 문제를 추가, 수정, 삭제할 수 있습니다.',
        tooltipPosition: 'right',
        buttonText: '완료',
        duration: 300,
      },
    ],
  },
  // Step 3: 오늘의 문제 (Bottom Recommendation)
  {
    stepNumber: 3,
    title: '오늘의 문제',
    sequences: [
      {
        type: 'd',
        dialogMessages: ['이제 맞춤형 문제 추천 기능을 체험해보겠습니다.', '사이드바의 "오늘의 문제" 버튼을 클릭해주세요.'],
        dialogButtons: [{ text: '다음', action: 'next' }],
      },
      {
        type: 'u',
        waitForEvent: 'click',
        eventTarget: '[data-onboarding-id="recommend-button"]',
        targetSelector: '[data-onboarding-id="recommend-button"]',
        message: '이 버튼을 클릭해보세요!',
        tooltipPosition: 'right',
        buttonText: '클릭해주세요',
        highlightAnimation: 'pulse',
        duration: 300,
      },
      {
        type: 'f',
        targetSelector: '[data-onboarding-id="bottom-recommend"]',
        message: ['여기서 당신의 실력과 목표에 맞는 문제를 추천받을 수 있습니다.', '좌측의 "추천 받기" 버튼을 클릭해보세요.'],
        tooltipPosition: 'top',
        buttonText: '다음',
        duration: 300,
      },
      {
        type: 'u',
        waitForEvent: 'click',
        eventTarget: '[data-onboarding-id="recommend-receive-button"]',
        targetSelector: '[data-onboarding-id="recommend-receive-button"]',
        message: '이 버튼을 클릭하면 맞춤형 알고리즘 문제가 추천됩니다!',
        tooltipPosition: 'right',
        buttonText: '클릭해주세요',
        highlightAnimation: 'pulse',
        duration: 300,
      },
      {
        type: 'f',
        targetSelector: '[data-onboarding-id="recommend-answer"]',
        message: ['추천된 문제들입니다!', '각 문제를 클릭하면 백준 사이트로 이동하며,', '"문제 등록" 버튼으로 캘린더에 일정을 추가할 수 있습니다.'],
        tooltipPosition: 'top',
        buttonText: '완료',
        duration: 300,
      },
    ],
  },
  // Step 4: Top Tierbar (티어 정보)
  {
    stepNumber: 4,
    title: 'Top Tierbar',
    sequences: [
      {
        type: 'd',
        dialogMessages: ['이번에는 티어 정보를 확인해보겠습니다.'],
        dialogButtons: [{ text: '다음', action: 'next' }],
      },
      {
        type: 's',
        duration: 300,
        systemAction: () => {
          console.log('Bottom Section 닫기');
        },
      },
      {
        type: 'u',
        waitForEvent: 'click',
        eventTarget: '[data-onboarding-id="tierbar-button"]',
        targetSelector: '[data-onboarding-id="tierbar-button"]',
        message: '티어 버튼을 클릭하면 현재 티어와 진행 상황을 확인할 수 있습니다.',
        tooltipPosition: 'right',
        buttonText: '클릭해보세요',
        highlightAnimation: 'pulse',
        duration: 300,
      },
      {
        type: 'f',
        targetSelector: '[data-onboarding-id="top-tierbar"]',
        message: '현재 티어와 다음 티어까지의 진행도를 확인할 수 있습니다.',
        tooltipPosition: 'bottom',
        buttonText: '다음',
        duration: 300,
      },
    ],
  },
  // Step 5: Top Streakbar (스트릭 정보)
  {
    stepNumber: 5,
    title: 'Top Streakbar',
    sequences: [
      {
        type: 'd',
        dialogMessages: ['이번에는 스트릭 정보를 확인해보겠습니다.'],
        dialogButtons: [{ text: '다음', action: 'next' }],
      },
      {
        type: 's',
        duration: 300,
        systemAction: () => {
          console.log('Top Section을 Streak으로 변경');
        },
      },
      {
        type: 'f',
        targetSelector: '[data-onboarding-id="top-streakbar"]',
        message: ['지난 1년간의 문제 풀이 기록을 한눈에 확인할 수 있습니다.', '꾸준히 문제를 풀어 스트릭을 이어가보세요!'],
        tooltipPosition: 'bottom',
        buttonText: '완료',
        duration: 300,
      },
    ],
  },
  // Step 6: Tag Dashboard (유형별 숙련도)
  {
    stepNumber: 6,
    title: 'Tag Dashboard',
    sequences: [
      {
        type: 'd',
        dialogMessages: ['이제 유형별 숙련도 대시보드를 확인해보겠습니다.'],
        dialogButtons: [{ text: '다음', action: 'next' }],
      },
      {
        type: 's',
        duration: 300,
        systemAction: () => {
          console.log('Top Section 닫기');
        },
      },
      {
        type: 'u',
        waitForEvent: 'click',
        eventTarget: '[data-onboarding-id="dashboard-button"]',
        targetSelector: '[data-onboarding-id="dashboard-button"]',
        message: '유형별 숙련도 버튼을 클릭하면 알고리즘 유형별 실력을 확인할 수 있습니다.',
        tooltipPosition: 'right',
        buttonText: '클릭해보세요',
        highlightAnimation: 'pulse',
        duration: 300,
      },
      {
        type: 'f',
        targetSelector: '[data-onboarding-id="first-tag-card"]',
        message: '각 유형별로 풀이 현황과 진행도를 확인할 수 있습니다.',
        tooltipPosition: 'right',
        buttonText: '완료',
        duration: 300,
      },
    ],
  },
  // Step 7: Refresh Button (프로필 갱신)
  {
    stepNumber: 7,
    title: 'Refresh Button',
    sequences: [
      {
        type: 'd',
        dialogMessages: ['프로필 갱신 기능을 알아보겠습니다.'],
        dialogButtons: [{ text: '다음', action: 'next' }],
      },
      {
        type: 'f',
        targetSelector: '[data-onboarding-id="refresh-button"]',
        message: '백준에서 새로 푼 문제가 있다면, 이 버튼으로 프로필을 갱신할 수 있습니다.',
        tooltipPosition: 'right',
        buttonText: '완료',
        duration: 300,
      },
    ],
  },
  // Step 8: 가입일 이전 문제 등록하기
  {
    stepNumber: 8,
    title: '가입일 이전 문제 등록',
    sequences: [
      {
        type: 'd',
        dialogMessages: ['마지막으로, 가입 전에 풀었던 문제를 등록하는 방법을 알려드리겠습니다.'],
        dialogButtons: [{ text: '다음', action: 'next' }],
      },
      {
        type: 'u',
        waitForEvent: 'click',
        eventTarget: '[data-onboarding-id="add-prev-problems-button"]',
        targetSelector: '[data-onboarding-id="add-prev-problems-button"]',
        message: '이 버튼을 클릭하면 과거에 풀었던 문제를 등록할 수 있습니다.',
        tooltipPosition: 'right',
        buttonText: '클릭해보세요',
        highlightAnimation: 'pulse',
        duration: 200,
      },
      {
        type: 'f',
        targetSelector: '[data-onboarding-id="open-baekjoon-button"]',
        message: ['이 버튼을 클릭하면 백준 채점현황 페이지가 열립니다.', '거기서 HTML을 복사하여 과거 풀이 기록을 등록할 수 있어요.'],
        tooltipPosition: 'right',
        buttonText: '다음',
        duration: 300,
      },
      {
        type: 'f',
        targetSelector: '[data-onboarding-id="paste-area"]',
        message: ['백준에서 복사한 HTML을 이곳에 붙여넣으면 자동으로 문제가 등록됩니다.', '최초 가입 후 가장 먼저 해야 할 작업입니다!'],
        tooltipPosition: 'top',
        buttonText: '완료',
        duration: 300,
      },
      {
        type: 's',
        duration: 200,
        systemAction: () => {
          console.log('모달 닫기');
        },
      },
    ],
  },
  // Step 9는 향후 구현
];
