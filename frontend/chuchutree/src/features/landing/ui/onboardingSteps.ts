/**
 * 온보딩 플로우 데이터 정의
 */

export type SequenceType = 'f' | 'd' | 's' | 'u' | 'init';

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
  // Step 1: 시작 페이지
  {
    stepNumber: 1,
    title: '시작 페이지',
    sequences: [
      {
        type: 'init',
      },
      {
        type: 'd',
        dialogMessages: ['ChuChuTree에 오신 것을 환영합니다!', '지금부터 주요 기능들을 살펴보겠습니다.'],
        dialogButtons: [{ text: '시작하기', action: 'start' }],
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
        message: '해결한 문제와 풀어야 할 문제가 기록됩니다.',
        tooltipPosition: 'right',
        buttonText: '다음',
        duration: 300,
      },
      {
        type: 'f',
        targetSelector: '[data-onboarding-id="calendar-sidebar-solved"]',
        message: '해결한 문제들을 확인할 수 있습니다.',
        tooltipPosition: 'right',
        buttonText: '다음',
        duration: 300,
      },
      {
        type: 'f',
        targetSelector: '[data-onboarding-id="calendar-sidebar-scheduled"]',
        message: '오늘 풀 문제를 기록 할 수 있습니다.',
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
        type: 'u',
        waitForEvent: 'click',
        eventTarget: '[data-onboarding-id="recommend-button"]',
        targetSelector: '[data-onboarding-id="recommend-button"]',
        message: '나만의 문제를 추천 받을 수 있습니다',
        tooltipPosition: 'right',
        buttonText: '주사위를 클릭해보세요!',
        highlightAnimation: 'pulse',
        duration: 300,
      },
      {
        type: 'f',
        targetSelector: '[data-onboarding-id="bottom-recommend"]',
        message: '나의 실력과 목표에 맞는 문제를 추천받을 수 있습니다.',
        tooltipPosition: 'top',
        buttonText: '다음',
        duration: 300,
      },
      {
        type: 'u',
        waitForEvent: 'click',
        eventTarget: '[data-onboarding-id="recommend-receive-button"]',
        targetSelector: '[data-onboarding-id="recommend-receive-button"]',
        message: '맞춤형 알고리즘 문제가 추천됩니다!',
        tooltipPosition: 'right',
        buttonText: '추천받기를 클릭해보세요!',
        highlightAnimation: 'pulse',
        duration: 300,
      },
      {
        type: 'f',
        targetSelector: '[data-onboarding-id="recommend-answer"]',
        message: ['추천된 문제들입니다!', '문제를 클릭하면 백준 사이트로 이동하며,', '"문제 등록"으로 캘린더에 일정을 추가할 수 있습니다.'],
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
        type: 'u',
        waitForEvent: 'click',
        eventTarget: '[data-onboarding-id="tierbar-button"]',
        targetSelector: '[data-onboarding-id="tierbar-button"]',
        message: '나의 티어와 진행 상황도 확인할 수 있습니다.',
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
        type: 'u',
        waitForEvent: 'click',
        eventTarget: '[data-onboarding-id="streakbar-button"]',
        targetSelector: '[data-onboarding-id="streakbar-button"]',
        message: '나의 1년 기록도 확인할 수 있습니다.',
        tooltipPosition: 'right',
        buttonText: '클릭해보세요',
        highlightAnimation: 'pulse',
        duration: 300,
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
        dialogMessages: ['이제 나만의 알고리즘을 확인해보겠습니다.'],
        dialogButtons: [{ text: '다음', action: 'next' }],
      },
      {
        type: 's',
        duration: 300,
        systemAction: () => {},
      },
      {
        type: 'u',
        waitForEvent: 'click',
        eventTarget: '[data-onboarding-id="dashboard-button"]',
        targetSelector: '[data-onboarding-id="dashboard-button"]',
        message: '나의 알고리즘 유형별 실력을 확인할 수 있습니다.',
        tooltipPosition: 'right',
        buttonText: '클릭해보세요',
        highlightAnimation: 'pulse',
        duration: 300,
      },
      {
        type: 'f',
        targetSelector: '[data-onboarding-id="first-tag-card"]',
        message: ['유형별로 날짜, 풀이 수, 등급을 확인할 수 있습니다.', 'Locked ≫ Intermediate ≫ Advanced ≫ Master', '모든 유형에 Master를 달성해보세요!'],
        tooltipPosition: 'right',
        buttonText: '완료',
        duration: 300,
      },
    ],
  },
  // Step 7: Refresh Button (프로필 갱신) + 가입일 이전 문제 등록하기
  {
    stepNumber: 7,
    title: 'Refresh Button and 가입일 이전 문제 등록',
    sequences: [
      {
        type: 'f',
        targetSelector: '[data-onboarding-id="refresh-button"]',
        message: '백준에서 새로 푼 문제가 있다면, 프로필을 갱신해야 합니다.',
        tooltipPosition: 'right',
        buttonText: '완료',
        duration: 300,
      },
      {
        type: 'f',
        targetSelector: '[data-onboarding-id="add-prev-problems-button"]',
        message: ['첫 가입 후에는 꼭!', ' 가입 전에 풀었던 문제들을 등록할 수 있습니다.'],
        tooltipPosition: 'right',
        buttonText: '완료',
        duration: 300,
      },
    ],
  },
  // Step 9: 마무리
  {
    stepNumber: 8,
    title: '마무리',
    sequences: [
      {
        type: 'd',
        dialogMessages: ['튜토리얼이 완료되었습니다! 🎉', '이제 ChuChuTree의 모든 기능을 사용할 수 있습니다.', '계속 튜토리얼 화면에서 둘러보시거나, \n로그인하고 ChuChuTree를 시작해보세요!'],
        dialogButtons: [
          { text: '더 둘러보기', action: 'next' },
          { text: '로그인하고 시작하기', action: 'login' },
        ],
      },
    ],
  },
];
