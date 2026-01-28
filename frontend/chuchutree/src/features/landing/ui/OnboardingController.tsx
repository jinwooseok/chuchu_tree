'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useOnboardingStore } from '@/lib/store/onboarding';
import { useLayoutStore } from '@/lib/store/layout';
import { ONBOARDING_STEPS } from './onboardingSteps';
import { OnboardingBackdrop } from './OnboardingBackdrop';
import { OnboardingDialog } from './OnboardingDialog';

export function OnboardingController() {
  const router = useRouter();
  const { currentStep, nextStep, skipOnboarding, completeOnboarding } = useOnboardingStore();
  const { setTopSection, setCenterSection, toggleBottomSection, bottomSection } = useLayoutStore();

  const [currentSequence, setCurrentSequence] = useState(0);

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
      <OnboardingBackdrop />
      {sequenceData.type === 'd' && sequenceData.dialogMessages && sequenceData.dialogButtons && (
        <OnboardingDialog messages={sequenceData.dialogMessages} buttons={sequenceData.dialogButtons} onButtonClick={handleDialogButtonClick} />
      )}
      {/* 향후 f, u 타입 추가 */}
    </>
  );
}
