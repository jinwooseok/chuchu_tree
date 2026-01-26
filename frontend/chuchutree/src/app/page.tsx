'use client';

import { ThemeButton } from '@/shared/ui';
import { useRouter } from 'next/navigation';
import Image from 'next/image';

export default function LandingPage() {
  const router = useRouter();
  const handleLogoClick = () => {
    router.push('/chu');
  };
  const handleSignInClick = () => {
    router.push('/sign-in');
  };
  return (
    <div className="bg-background flex h-screen w-screen items-center justify-center p-4">
      <div className="bg-innerground-white flex h-full w-full max-w-4xl flex-col overflow-auto rounded-xl px-8 py-4">
        <div className="mb-4 flex items-center justify-between select-none">
          <div className="flex cursor-pointer items-center gap-2" onClick={handleLogoClick}>
            <Image src="/logo/logo.svg" alt="logo" width={16} height={16} />
            <div>ChuChuTree</div>
          </div>
          <div className="min-w-22">
            <ThemeButton />
          </div>
        </div>
        <h1 className="h-50 text-center">임시 공개 랜딩 페이지</h1>
        <button onClick={handleLogoClick}>입장하기</button>
        <button onClick={handleSignInClick}>로그인하러가기</button>
        {/* 로그인 버튼 등 */}
      </div>
    </div>
  );
}
