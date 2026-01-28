'use client';

import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

interface OnboardingTooltipProps {
  message: string | string[];
  position: { x: number; y: number };
  placement: 'top' | 'bottom' | 'left' | 'right';
  buttonText?: string;
  onButtonClick?: () => void;
}

export function OnboardingTooltip({ message, position, placement, buttonText, onButtonClick }: OnboardingTooltipProps) {
  const messages = Array.isArray(message) ? message : [message];

  // 화살표 위치 계산
  const arrowClasses = {
    top: 'bottom-[-8px] left-1/2 -translate-x-1/2 border-t-background border-l-transparent border-r-transparent border-b-transparent',
    bottom: 'top-[-8px] left-1/2 -translate-x-1/2 border-b-background border-l-transparent border-r-transparent border-t-transparent',
    left: 'right-[-8px] top-1/2 -translate-y-1/2 border-l-background border-t-transparent border-b-transparent border-r-transparent',
    right: 'left-[-8px] top-1/2 -translate-y-1/2 border-r-background border-t-transparent border-b-transparent border-l-transparent',
  };

  return (
    <div
      className="bg-background fixed z-50 max-w-sm rounded-lg border p-4 shadow-lg"
      style={{
        left: `${position.x}px`,
        top: `${position.y}px`,
      }}
    >
      {/* 화살표 */}
      <div className={cn('absolute h-0 w-0 border-8', arrowClasses[placement])} />

      {/* 메시지 */}
      <div className="space-y-2">
        {messages.map((msg, index) => (
          <p key={index} className={cn('text-sm', index === 0 ? 'font-semibold' : 'text-muted-foreground')}>
            {msg}
          </p>
        ))}
      </div>

      {/* 버튼 */}
      {buttonText && onButtonClick && (
        <div className="mt-3">
          <Button onClick={onButtonClick} size="sm" className="w-full">
            {buttonText}
          </Button>
        </div>
      )}
    </div>
  );
}
