'use client';

import { SocialWays } from '@/shared/constants/auth';
import { ThemeButton } from '@/shared/ui';
import Image from 'next/image';
import { useTheme } from 'next-themes';
import { useSyncExternalStore } from 'react';
import { useRouter } from 'next/navigation';
import { AppTooltip } from '@/components/custom/tooltip/AppTooltip';

type SocialWay = (typeof SocialWays)[number];

// useSyncExternalStore를 위한 빈 subscribe 함수
const subscribe = () => () => {};

const SocialLoginButton = ({ theme, ...props }: SocialWay & { theme: string }) => {
  const handleLogin = () => {
    const baseUrl = process.env.NEXT_PUBLIC_API_URL || '';
    const loginPath = `/api/v1/auth/login/${props.en}`;

    // 개발 환경에서는 localhost로 redirect되도록 설정
    const redirectUrl = process.env.NODE_ENV === 'development' ? '?redirectUrl=http://localhost:3000' : '';

    window.location.href = `${baseUrl}${loginPath}${redirectUrl}`;
  };
  return (
    <button onClick={handleLogin} className="hover:bg-background/50 border-innerground-darkgray relative flex w-80 cursor-pointer items-center justify-between rounded border px-2 py-2 text-sm">
      <Image src={`/socialicon/${props.en}_${theme}.svg`} alt={`social icon ${props.en}_${theme}`} width={24} height={24} className="absolute left-2" />
      <div className="flex-1 text-center">{props.kr}로 시작하기</div>
    </button>
  );
};

export default function SignInClient() {
  const { resolvedTheme } = useTheme();
  const router = useRouter();
  // SSR 안전한 mounted 상태 체크
  const mounted = useSyncExternalStore(
    subscribe,
    () => true, // 클라이언트에서는 항상 true
    () => false, // 서버에서는 항상 false
  );
  return (
    <div className="bg-innerground-white flex h-full w-full flex-col rounded-xl p-4">
      <div className="flex items-center justify-between">
        <AppTooltip content="튜토리얼 하러가기" side="right" delayDuration={300}>
          <div className="flex cursor-pointer items-center gap-2" onClick={() => router.push('/')}>
            <Image src="/logo/logo.svg" alt="logo" width={16} height={16} />
            <div>ChuChuTree</div>
          </div>
        </AppTooltip>
        <div className="flex items-center gap-2">
          <div className="min-w-22">
            <ThemeButton />
          </div>
          <button className="hover:bg-muted cursor-pointer rounded-sm p-1 text-sm" onClick={() => router.push('/')}>
            튜토리얼
          </button>
        </div>
      </div>
      <div className="flex flex-1 flex-col items-center justify-center">
        {!mounted ? (
          <div className="flex flex-col gap-2">
            <div className="mb-4 cursor-default select-none">
              <div className="font-semibold">나만의 알고리즘 캘린더</div>
              <div className="text-muted-foreground">ChuChuTree 로그인</div>
            </div>
            {SocialWays.map((way) => (
              <SocialLoginButton key={way.en} {...way} theme={'light'} />
            ))}
          </div>
        ) : (
          <div className="flex flex-col gap-2">
            <div className="mb-4 cursor-default select-none">
              <div className="font-semibold">나만의 알고리즘 캘린더</div>
              <div className="text-muted-foreground">ChuChuTree 로그인</div>
            </div>
            {SocialWays.map((way) => (
              <SocialLoginButton key={way.en} {...way} theme={resolvedTheme || 'light'} />
            ))}
          </div>
        )}
        <div className="text-muted-foreground mt-4 flex cursor-default gap-1 text-xs">
          <div className="text-muted-foreground mx-1 mt-2 flex w-80 cursor-default justify-center gap-1 text-xs">
            <div>
              <span>계속 진행하면 만 14세 이상이며, </span>
              <span
                className="hover:text-primary/60 cursor-pointer underline"
                onClick={() => {
                  router.push('/policies/terms-of-service');
                }}
              >
                이용약관
              </span>
              <span> 및 </span>
              <span
                className="hover:text-primary/60 cursor-pointer underline"
                onClick={() => {
                  router.push('/policies/privacy');
                }}
              >
                개인정보처리방침
              </span>
              <span>을 이해하고 동의하는 것으로 간주됩니다.</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
