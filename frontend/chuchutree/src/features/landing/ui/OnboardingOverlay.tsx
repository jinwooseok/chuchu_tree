'use client';

import { useOnboardingStore } from '@/lib/store/onboarding';
import { Button } from '@/components/ui/button';

const ONBOARDING_MESSAGES = [
  {
    step: 1,
    title: '환영합니다! 🎉',
    description: 'ChuChuTree는 알고리즘 문제 풀이를 체계적으로 관리하고 추천받을 수 있는 서비스입니다.',
  },
  {
    step: 2,
    title: '나만의 알고리즘 캘린더 📅',
    description: '문제 풀이 일정을 캘린더로 관리하고, 유형별 숙련도를 대시보드로 확인할 수 있습니다.',
  },
  {
    step: 3,
    title: '맞춤형 문제 추천 💡',
    description: '당신의 실력과 목표에 맞는 문제를 매일 추천받아보세요. 지금 바로 시작해보세요!',
  },
];

export function OnboardingOverlay() {
  const { currentStep, nextStep, skipOnboarding, completeOnboarding } = useOnboardingStore();

  const currentMessage = ONBOARDING_MESSAGES[currentStep - 1];
  const isLastStep = currentStep === 3;

  const handleNext = () => {
    if (isLastStep) {
      completeOnboarding();
    } else {
      nextStep();
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div className="bg-background mx-4 max-w-md rounded-lg border p-8 shadow-lg">
        {/* 단계 인디케이터 */}
        <div className="mb-4 flex justify-center gap-2">
          {[1, 2, 3].map((step) => (
            <div key={step} className={`h-2 w-8 rounded-full transition-colors ${step === currentStep ? 'bg-primary' : 'bg-muted'}`} />
          ))}
        </div>

        {/* 메시지 */}
        <div className="mb-6 text-center">
          <h2 className="mb-3 text-2xl font-bold">{currentMessage.title}</h2>
          <p className="text-muted-foreground">{currentMessage.description}</p>
        </div>

        {/* 버튼 */}
        <div className="flex justify-between gap-3">
          <Button variant="outline" onClick={skipOnboarding} className="flex-1">
            건너뛰기
          </Button>
          <Button onClick={handleNext} className="flex-1">
            {isLastStep ? '시작하기' : '다음'}
          </Button>
        </div>

        {/* 단계 표시 */}
        <p className="text-muted-foreground mt-4 text-center text-sm">
          {currentStep} / 3
        </p>
      </div>
    </div>
  );
}
