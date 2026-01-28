'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useOnboardingStore } from '@/lib/store/onboarding';
import { useLayoutStore } from '@/lib/store/layout';
import { ONBOARDING_STEPS } from './onboardingSteps';
import { OnboardingBackdrop } from './OnboardingBackdrop';
import { OnboardingDialog } from './OnboardingDialog';
import { OnboardingSpotlight } from './OnboardingSpotlight';
import { getElementPosition } from './onboardingHelpers';

export function OnboardingController() {
  const router = useRouter();
  const { currentStep, nextStep, skipOnboarding, completeOnboarding } = useOnboardingStore();
  const { setTopSection, setCenterSection, toggleBottomSection, bottomSection } = useLayoutStore();

  const [currentSequence, setCurrentSequence] = useState(0);
  const [spotlightTarget, setSpotlightTarget] = useState<{ x: number; y: number; width: number; height: number } | null>(null);

  // Spotlight 위치 업데이트 핸들러
  const handlePositionChange = (position: { x: number; y: number; width: number; height: number } | null) => {
    setSpotlightTarget(position);
  };

  // 현재 step과 sequence 데이터
  const currentStepData = ONBOARDING_STEPS[currentStep - 1];
  const sequenceData = currentStepData?.sequences[currentSequence];

  // 다음 sequence로 이동
  const goToNextSequence = () => {
    if (currentSequence < currentStepData.sequences.length - 1) {
      setCurrentSequence((prev) => prev + 1);
    } else {
      // 마지막 sequence면 다음 step으로
      if (currentStep < ONBOARDING_STEPS.length) {
        nextStep();
        setCurrentSequence(0);
      } else {
        // 마지막 step이면 온보딩 완료
        completeOnboarding();
      }
    }
  };

  // sequence가 변경될 때 처리
  useEffect(() => {
    if (!sequenceData) return;

    // 's' 타입: 시스템 동작 실행
    if (sequenceData.type === 's') {
      // Step 1의 레이아웃 초기화
      if (currentStep === 1 && currentSequence === 1) {
        setTopSection(null);
        setCenterSection('calendar');
        // bottomSection이 열려있으면 닫기
        if (bottomSection === 'recommend') {
          toggleBottomSection();
        }
      }

      // systemAction이 있으면 실행
      if (sequenceData.systemAction) {
        sequenceData.systemAction();
      }

      // duration 후 자동으로 다음 sequence로
      const timer = setTimeout(() => {
        goToNextSequence();
      }, sequenceData.duration || 0);

      return () => clearTimeout(timer);
    }

    // 'f' 타입: spotlight 위치는 OnboardingSpotlight에서 계산하여 전달받음
    // 별도 처리 불필요

    // 'u' 타입: 사용자 인터랙션 대기
    if (sequenceData.type === 'u' && sequenceData.eventTarget) {
      // spotlight 위치는 OnboardingSpotlight에서 계산하여 전달받음
      // 클릭 이벤트 리스너만 부착
      const handleClick = () => {
        // 실제 버튼 기능이 동작하도록 preventDefault/stopPropagation 제거
        // 클릭 후 약간의 딜레이를 두고 다음 sequence로 이동 (버튼 동작 완료 후)
        setTimeout(() => {
          goToNextSequence();
        }, 100);
      };

      const targetElement = document.querySelector(sequenceData.eventTarget);
      if (targetElement) {
        targetElement.addEventListener('click', handleClick);
      }

      return () => {
        if (targetElement) {
          targetElement.removeEventListener('click', handleClick);
        }
      };
    }

    // 'd', 's' 타입이면 spotlight 제거
    if (sequenceData.type === 'd') {
      setSpotlightTarget(null);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [currentStep, currentSequence, bottomSection]);

  // 다이얼로그 버튼 클릭 처리
  const handleDialogButtonClick = (action: string) => {
    switch (action) {
      case 'next':
      case 'start':
        goToNextSequence();
        break;
      case 'skip':
        skipOnboarding();
        break;
      case 'login':
        completeOnboarding();
        router.push('/sign-in');
        break;
    }
  };

  if (!sequenceData) {
    return null;
  }

  // 렌더링
  return (
    <>
      <OnboardingBackdrop spotlightTarget={spotlightTarget} allowInteraction={sequenceData.type === 'u'} />

      {sequenceData.type === 'd' && sequenceData.dialogMessages && sequenceData.dialogButtons && (
        <OnboardingDialog messages={sequenceData.dialogMessages} buttons={sequenceData.dialogButtons} onButtonClick={handleDialogButtonClick} />
      )}

      {sequenceData.type === 'f' && sequenceData.targetSelector && sequenceData.message && (
        <OnboardingSpotlight
          targetSelector={sequenceData.targetSelector}
          message={sequenceData.message}
          tooltipPosition={sequenceData.tooltipPosition || 'right'}
          buttonText={sequenceData.buttonText}
          onNext={goToNextSequence}
          highlightAnimation={sequenceData.highlightAnimation}
          onPositionChange={handlePositionChange}
        />
      )}

      {sequenceData.type === 'u' && (sequenceData.targetSelector || sequenceData.eventTarget) && sequenceData.message && (
        <OnboardingSpotlight
          targetSelector={sequenceData.targetSelector || sequenceData.eventTarget!}
          message={sequenceData.message}
          tooltipPosition={sequenceData.tooltipPosition || 'right'}
          buttonText={sequenceData.buttonText || '클릭해주세요'}
          onNext={() => {}} // 버튼은 표시만 하고 실제 동작 없음
          highlightAnimation={sequenceData.highlightAnimation || 'pulse'}
          onPositionChange={handlePositionChange}
        />
      )}
    </>
  );
}
