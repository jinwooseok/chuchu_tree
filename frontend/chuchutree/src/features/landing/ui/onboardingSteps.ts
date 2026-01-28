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
        dialogButtons: [
          { text: '시작하기', action: 'start' },
          { text: '건너뛰기', action: 'skip' },
        ],
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
  // Step 4-9는 향후 구현
];
