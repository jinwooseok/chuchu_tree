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
        dialogMessages: [
          '이곳은 캘린더 화면입니다.',
          '문제 풀이 일정을 한눈에 확인하고 관리할 수 있습니다.',
        ],
        dialogButtons: [{ text: '다음', action: 'next' }],
      },
      // 나머지 sequence는 2단계에서 구현
    ],
  },
  // Step 3-9는 향후 구현
];
