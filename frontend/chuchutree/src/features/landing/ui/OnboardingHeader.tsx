'use client';

import { Button } from '@/components/ui/button';
import { useOnboardingStore } from '@/lib/store/onboarding';
import { ONBOARDING_STEPS } from './onboardingSteps';
import { X, ChevronRight } from 'lucide-react';

export function OnboardingHeader() {
  const { currentStep, skipCurrentStep, completeOnboarding } = useOnboardingStore();
  const totalSteps = ONBOARDING_STEPS.length;

  return (
    <div className="fixed top-4 right-4 z-60 flex items-center gap-3">
      {/* 현재 단계 표시 */}
      <div className="bg-background/95 flex items-center gap-2 rounded-lg border px-4 py-2 shadow-lg backdrop-blur-sm">
        <span className="text-sm font-medium">
          Step {currentStep} / {totalSteps}
        </span>
      </div>

      {/* 건너뛰기 버튼 */}
      <Button variant="outline" size="sm" onClick={skipCurrentStep} className="gap-1">
        <span>건너뛰기</span>
        <ChevronRight className="h-4 w-4" />
      </Button>

      {/* 종료 버튼 */}
      <Button variant="outline" size="sm" onClick={completeOnboarding} className="gap-1">
        <X className="h-4 w-4" />
        <span>종료</span>
      </Button>
    </div>
  );
}
