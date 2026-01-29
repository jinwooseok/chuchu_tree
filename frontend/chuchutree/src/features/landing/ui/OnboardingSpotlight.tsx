'use client';

import { useState, useEffect } from 'react';
import { OnboardingTooltip } from './OnboardingTooltip';
import { getElementPosition, calculateTooltipPosition, scrollToElement, waitForElement, ElementPosition } from './onboardingHelpers';

interface OnboardingSpotlightProps {
  targetSelector: string;
  message: string | string[];
  tooltipPosition: 'top' | 'bottom' | 'left' | 'right';
  buttonText?: string;
  onNext: () => void;
  highlightAnimation?: 'pulse' | 'arrow' | 'none';
  onPositionChange?: (position: ElementPosition | null) => void; // 위치 변경 콜백
}

export function OnboardingSpotlight({ targetSelector, message, tooltipPosition, buttonText = '다음', onNext, highlightAnimation = 'pulse', onPositionChange }: OnboardingSpotlightProps) {
  const [targetPos, setTargetPos] = useState<ElementPosition | null>(null);
  const [tooltipPos, setTooltipPos] = useState<{ x: number; y: number; placement: 'top' | 'bottom' | 'left' | 'right' } | null>(null);

  useEffect(() => {
    let mounted = true;

    const setupSpotlight = async () => {
      try {
        // 요소가 렌더링될 때까지 대기
        await waitForElement(targetSelector, 5000);

        if (!mounted) return;

        // 요소로 스크롤
        scrollToElement(targetSelector);

        // 약간의 딜레이 후 위치 계산 (스크롤 애니메이션 대기)
        setTimeout(() => {
          if (!mounted) return;

          const position = getElementPosition(targetSelector);
          if (position) {
            setTargetPos(position);

            // Tooltip 위치 계산
            const { adjustedPlacement, ...tooltipCoords } = calculateTooltipPosition(position, tooltipPosition);
            setTooltipPos({ ...tooltipCoords, placement: adjustedPlacement });
          }
        }, 300);
      } catch (error) {
        console.error('Spotlight setup failed:', error);
      }
    };

    setupSpotlight();

    // 리사이즈 시 위치 재계산
    const handleResize = () => {
      const position = getElementPosition(targetSelector);
      if (position) {
        setTargetPos(position);
        const { adjustedPlacement, ...tooltipCoords } = calculateTooltipPosition(position, tooltipPosition);
        setTooltipPos({ ...tooltipCoords, placement: adjustedPlacement });
      }
    };

    window.addEventListener('resize', handleResize);

    return () => {
      mounted = false;
      window.removeEventListener('resize', handleResize);
    };
  }, [targetSelector, tooltipPosition]);

  // targetPos가 변경될 때마다 부모에게 알림
  useEffect(() => {
    if (onPositionChange) {
      onPositionChange(targetPos);
    }
  }, [targetPos, onPositionChange]);

  if (!targetPos || !tooltipPos) {
    return null;
  }

  return (
    <>
      {/* Spotlight 강조 효과 */}
      <div
        className="border-primary pointer-events-none fixed z-45 rounded-md border-2"
        style={{
          left: `${targetPos.x - 4}px`,
          top: `${targetPos.y - 4}px`,
          width: `${targetPos.width + 8}px`,
          height: `${targetPos.height + 8}px`,
          animation: highlightAnimation === 'pulse' ? 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite' : 'none',
        }}
      />

      {/* Tooltip */}
      <OnboardingTooltip message={message} position={{ x: tooltipPos.x, y: tooltipPos.y }} placement={tooltipPos.placement} buttonText={buttonText} onButtonClick={onNext} />
    </>
  );
}
