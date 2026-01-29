'use client';

import { Button } from '@/components/ui/button';

interface OnboardingDialogProps {
  messages: string[];
  buttons: Array<{
    text: string;
    action: 'next' | 'skip' | 'start' | 'login';
  }>;
  onButtonClick: (action: string) => void;
}

export function OnboardingDialog({ messages, buttons, onButtonClick }: OnboardingDialogProps) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="bg-background mx-4 max-w-md rounded-lg border p-8 shadow-lg">
        {/* 메시지 */}
        <div className="mb-6 space-y-3 text-center">
          {messages.map((message, index) => (
            <p key={index} className={index === 0 ? 'text-xl whitespace-pre-wrap' : 'text-muted-foreground whitespace-pre-wrap'}>
              {message}
            </p>
          ))}
        </div>

        {/* 버튼 */}
        <div className="flex justify-center gap-3">
          {buttons.map((button, index) => (
            <Button key={index} variant={button.action === 'skip' ? 'outline' : 'default'} onClick={() => onButtonClick(button.action)} className="flex-1">
              {button.text}
            </Button>
          ))}
        </div>
      </div>
    </div>
  );
}
