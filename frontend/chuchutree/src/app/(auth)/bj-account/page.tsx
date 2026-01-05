'use client';

import { ThemeButton } from '@/shared/ui';
import Image from 'next/image';
import { useState } from 'react';

export default function BjAccountRegistration() {
  const [bjHandle, setBjHandle] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!bjHandle.trim()) {
      alert('백준 아이디를 입력해주세요.');
      return;
    }

    setIsLoading(true);

    // TODO: API 연동 (나중에 구현)
    console.log('백준 아이디:', bjHandle);

    setIsLoading(false);
  };

  return (
    <div className="bg-innerground-white flex h-full w-full max-w-md flex-col rounded-xl p-8">
      <div className="mb-8 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Image src="/logo/logo.svg" alt="logo" width={16} height={16} className="h-6 w-6" />
          <div>ChuChuTree</div>
        </div>
        <div className="min-w-22">
          <ThemeButton />
        </div>
      </div>

      <div className="flex flex-1 flex-col justify-center">
        <div className="mb-8">
          <h1 className="mb-2 text-2xl font-semibold">백준 계정 등록</h1>
          <p className="text-muted-foreground text-sm">ChuChuTree 서비스를 이용하려면 백준 계정 연동이 필요합니다.</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label htmlFor="bjHandle" className="mb-2 block text-sm font-medium">
              백준 아이디 (Handle)
            </label>
            <input
              id="bjHandle"
              type="text"
              value={bjHandle}
              onChange={(e) => setBjHandle(e.target.value)}
              placeholder="백준 아이디를 입력하세요"
              className="focus:ring-primary w-full rounded-lg border border-gray-300 px-4 py-2 focus:border-transparent focus:ring-2 focus:outline-none"
              disabled={isLoading}
            />
            <p className="text-muted-foreground mt-2 text-xs">예: baekjoon (solved.ac 프로필의 Handle과 동일)</p>
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="bg-primary hover:bg-primary/90 w-full rounded-lg px-4 py-2 text-white transition-colors disabled:cursor-not-allowed disabled:bg-gray-300"
          >
            {isLoading ? '등록 중...' : '계정 등록'}
          </button>
        </form>

        <div className="mt-8 text-center">
          <p className="text-muted-foreground text-xs">
            백준 아이디는{' '}
            <a href="https://www.acmicpc.net" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline">
              www.acmicpc.net
            </a>
            에서 확인할 수 있습니다.
          </p>
        </div>
      </div>
    </div>
  );
}
