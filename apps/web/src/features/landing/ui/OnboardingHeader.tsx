'use client';

import { useOnboardingStore } from '@/lib/store/onboarding';
import { ONBOARDING_STEPS } from './onboardingSteps';
import { X, ChevronRight, ChevronLeft } from 'lucide-react';

export function OnboardingHeader() {
  const { currentStep, skipCurrentStep, completeOnboarding, prevStep } = useOnboardingStore();
  const totalSteps = ONBOARDING_STEPS.length;

  return (
    <div className="fixed top-4 right-4 z-60 flex h-10 items-center gap-3">
      {/* 현재 단계 표시 */}
      <div className="bg-background hover:bg-innerground-darkgray flex h-full cursor-pointer items-center gap-2 rounded-lg border px-4 select-none">
        <span className="text-sm font-medium">
          Step {currentStep} / {totalSteps}
        </span>
      </div>

      {/* 이전 버튼 */}
      {currentStep !== 1 && (
        <button onClick={prevStep} className="bg-background hover:bg-innerground-darkgray flex h-full cursor-pointer items-center gap-1 rounded-lg border pr-3 pl-4 select-none">
          <ChevronLeft className="h-4 w-4" />
          <span>돌아가기</span>
        </button>
      )}
      {/* 건너뛰기 버튼 */}
      <button onClick={skipCurrentStep} className="bg-background hover:bg-innerground-darkgray flex h-full cursor-pointer items-center gap-1 rounded-lg border pr-3 pl-4 select-none">
        <span>건너뛰기</span>
        <ChevronRight className="h-4 w-4" />
      </button>

      {/* 종료 버튼 */}
      <button onClick={completeOnboarding} className="bg-background hover:bg-innerground-darkgray flex h-full cursor-pointer items-center gap-1 rounded-lg border px-4 select-none">
        <X className="h-4 w-4" />
        <span>종료</span>
      </button>
    </div>
  );
}
