'use client';

import { ThemeButton } from '@/shared/ui';
import Image from 'next/image';
import { useState } from 'react';
import { useLinkBjAccount } from '@/entities/bj-account';
import { usePostTarget } from '@/entities/user';
import { useRouter } from 'next/navigation';
import { toast } from '@/lib/utils/toast';
import { TargetCode } from '@/shared/constants/tagSystem';
import { getErrorMessage } from '@/lib/utils/error';
import { TARGET_OPTIONS } from '@/shared/constants/target';
import { useLogout } from '@/entities/auth';

export default function BjAccountRegistrationClient() {
  const [bjHandle, setBjHandle] = useState('');
  const [selectedTarget, setSelectedTarget] = useState<TargetCode>('DAILY');
  const router = useRouter();

  const { mutate: postTarget, isPending: isPostTargetPending } = usePostTarget();

  const { mutate: linkBjAccount, isPending: isLinkBjAccountPending } = useLinkBjAccount({
    onSuccess: () => {
      // 백준 계정 등록 성공 후 목표 설정
      postTarget(
        { targetCode: selectedTarget },
        {
          onSuccess: () => {
            toast.success('계정이 등록되었습니다.');
            router.push('/');
          },
          onError: () => {
            toast.warning('계정은 등록되었으나 목표 설정에 실패했습니다.');
            router.push('/');
          },
        },
      );
    },
    onError: (error) => {
      const errorMessage = getErrorMessage(error, '계정 등록에 실패했습니다. 다시 시도해주세요.');
      toast.error(errorMessage);
    },
  });
  const { mutate: logout, isPending: isLogoutPending } = useLogout({
    onSuccess: () => {
      toast.success('로그아웃되었습니다.');
      router.push('/sign-in');
    },
    onError: () => {
      toast.error('로그아웃에 실패했습니다. 다시 시도해주세요.');
    },
  });

  const isPending = isLinkBjAccountPending || isPostTargetPending;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!bjHandle.trim()) {
      toast.info('백준 아이디를 입력해주세요.');
      return;
    }
    linkBjAccount({ bjAccount: bjHandle.trim() });
  };

  const handleLogout = () => {
    logout();
  };

  return (
    <div className="bg-innerground-white hide-scrollbar flex h-full w-full max-w-md flex-col overflow-auto rounded-xl px-8 py-4">
      <div className="mb-4 flex items-center justify-between">
        <div className="flex cursor-default items-center gap-2">
          <Image src="/logo/logo.svg" alt="logo" width={16} height={16} />
          <div>ChuChuTree</div>
        </div>
        <div className="min-w-22">
          <ThemeButton />
        </div>
      </div>

      <div className="flex flex-1 flex-col justify-center">
        <div className="mb-8">
          <h1 className="mb-2 cursor-default text-2xl font-semibold">백준 계정 등록</h1>
          <p className="text-muted-foreground cursor-default text-sm">ChuChuTree 서비스를 이용하려면 백준 계정 연동이 필요합니다.</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label htmlFor="bjHandle" className="mb-2 block text-sm">
              백준 아이디
            </label>
            <input
              id="bjHandle"
              type="text"
              value={bjHandle}
              onChange={(e) => setBjHandle(e.target.value)}
              placeholder="백준 아이디를 입력하세요"
              className="focus:ring-primary border-innerground-darkgray w-full rounded-lg border px-4 py-2 focus:border-transparent focus:ring-2 focus:outline-none"
              disabled={isPending}
            />
            <p className="text-muted-foreground mt-2 text-xs">예: baekjoon (solved.ac 프로필의 아이디와 동일)</p>
          </div>

          <div>
            <label className="mb-3 block text-sm">학습 목표</label>
            <div className="space-y-3">
              {TARGET_OPTIONS.map((option) => (
                <label
                  key={option.code}
                  className={`flex cursor-pointer items-start gap-3 rounded-lg border-2 p-4 transition-all ${
                    selectedTarget === option.code ? 'border-primary bg-primary/5' : 'border-innerground-darkgray hover:border-primary/50'
                  } ${isPending ? 'cursor-not-allowed opacity-50' : ''}`}
                >
                  <input
                    type="radio"
                    name="target"
                    value={option.code}
                    checked={selectedTarget === option.code}
                    onChange={(e) => setSelectedTarget(e.target.value as TargetCode)}
                    disabled={isPending}
                    className="text-primary focus:ring-primary mt-1 h-4 w-4"
                  />
                  <div className="flex-1">
                    <div className="mb-2 flex items-center gap-2">
                      <div className="font-medium">{option.label}</div>
                      <div className="text-muted-foreground text-xs">{option.description}</div>
                    </div>
                    <div className="text-muted-foreground text-xs">{option.description2}</div>
                  </div>
                </label>
              ))}
            </div>
          </div>

          <button
            type="submit"
            disabled={isPending}
            className="bg-primary hover:bg-primary/90 disabled:bg-muted-foreground w-full cursor-pointer rounded-lg px-4 py-2 text-white transition-colors disabled:cursor-not-allowed"
          >
            {isPending ? '등록 중...' : '계정 등록'}
          </button>
        </form>

        <div className="text-muted-foreground mt-6 flex items-center justify-center gap-2 text-center text-xs">
          <span>
            백준 아이디는{' '}
            <a href="https://www.acmicpc.net" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline">
              www.acmicpc.net
            </a>
            에서 확인할 수 있습니다.
          </span>
          <span className="cursor-default">|</span>
          <button
            className="hover:text-primary cursor-pointer"
            onClick={(e) => {
              e.preventDefault();
              handleLogout();
            }}
            disabled={isLogoutPending}
          >
            로그아웃
          </button>
        </div>
      </div>
    </div>
  );
}
