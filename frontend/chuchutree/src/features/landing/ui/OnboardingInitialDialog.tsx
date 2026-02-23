'use client';

import { Button } from '@/components/ui/button';
import { ThemeButton } from '@/shared/ui';
import Image from 'next/image';
import { useRouter } from 'next/navigation';

// const action =  'next' | 'skip' | 'start' | 'login';
interface Props {
  isLanding: boolean;
  onButtonClick: (action: string) => void;
}

export function OnboardingInitialDialog({ onButtonClick, isLanding }: Props) {
  const router = useRouter();
  return (
    <div className="bg-background fixed inset-0 z-50 h-screen w-screen p-4">
      <div className="bg-innerground-white flex h-full w-full flex-col items-center justify-center rounded-lg p-4">
        {/* 상단헤더 */}
        <div className="flex w-full items-center justify-between">
          <div className="flex cursor-default items-center gap-2">
            <Image src="/logo/logo.svg" alt="logo" width={16} height={16} />
            <div>ChuChuTree</div>
          </div>
          <div className="flex items-center gap-2">
            <div className="min-w-22">
              <ThemeButton />
            </div>
            {isLanding && (
              <button className="hover:bg-muted cursor-pointer rounded-sm p-1 text-sm" onClick={() => router.push('/sign-in')}>
                로그인
              </button>
            )}
          </div>
        </div>
        {/* 메인 */}
        <div className="flex flex-1 flex-col items-center justify-center gap-4">
          {/* 메시지 */}
          <div className="mb-6 space-y-3 text-center">
            <p className="text-4xl font-semibold">나에게 딱맞는 알고리즘 추천,</p>
            <p className="text-4xl font-semibold">매일 기록하는 알고리즘 캘린더</p>
            <p className="text-lg whitespace-pre-wrap">알고리즘 기록으로 최적의 알고리즘 문제를 추천받을 수 있습니다.</p>
            <p className="text-lg whitespace-pre-wrap">
              <span className="text-primary/60">ChuChuTree</span>에서, 가장 빠르고 효율적으로 최고의 실력에 도달할 수 있습니다.
            </p>
          </div>

          {/* 버튼 */}
          <div className="flex justify-center gap-3">
            <button onClick={() => onButtonClick('start')} className="bg-primary hover:bg-primary-hover cursor-pointer rounded-sm px-4 py-2 text-white duration-200 ease-in-out select-none">
              튜토리얼 시작하기
            </button>
            {isLanding && (
              <button onClick={() => router.push('/sign-in')} className="bg-primary/30 hover:bg-primary/20 text-primary cursor-pointer rounded-sm px-4 py-2 duration-200 ease-in-out select-none">
                로그인 하러가기
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
