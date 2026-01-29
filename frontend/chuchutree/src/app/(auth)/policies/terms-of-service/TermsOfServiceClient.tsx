'use client';

import { ThemeButton } from '@/shared/ui';
import Image from 'next/image';
import { useRouter } from 'next/navigation';
import ReactMarkdown from 'react-markdown';

interface TermsOfServiceClientProps {
  markdownContent: string;
}

export default function TermsOfServiceClient({ markdownContent }: TermsOfServiceClientProps) {
  const router = useRouter();

  const handleLogoClick = () => {
    router.push('/chu');
  };

  const handleNavigateToPrivacy = () => {
    router.push('/policies/privacy');
  };

  return (
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

      <div className="mb-6 flex items-center justify-between select-none">
        <div className="flex gap-2">
          <button className="bg-primary text-primary-foreground cursor-pointer rounded-lg px-4 py-2 text-sm font-medium" disabled>
            이용약관
          </button>
          <button
            onClick={handleNavigateToPrivacy}
            className="border-innerground-darkgray hover:bg-innerground-darkgray/10 cursor-pointer rounded-lg border px-4 py-2 text-sm font-medium transition-colors"
          >
            개인정보 처리방침
          </button>
        </div>
        <button onClick={handleLogoClick} className="bg-primary text-primary-foreground cursor-pointer rounded-lg px-4 py-2 text-sm font-medium">
          돌아가기
        </button>
      </div>

      <div className="flex flex-1 cursor-default flex-col select-none">
        <div className="mb-8">
          <h1 className="mb-2 cursor-default text-2xl font-semibold">서비스 이용약관</h1>
          <p className="text-muted-foreground cursor-default text-sm">시행일자: 2026.01.22</p>
        </div>
        <div className="prose prose-sm dark:prose-invert max-w-none">
          <ReactMarkdown
            components={{
              h1: ({ children }) => <h1 className="mt-6 mb-4 text-xl font-bold">{children}</h1>,
              h2: ({ children }) => <h2 className="mt-5 mb-3 text-lg font-semibold">{children}</h2>,
              h3: ({ children }) => <h3 className="mt-4 mb-2 text-lg font-semibold">{children}</h3>,
              p: ({ children }) => <p className="mb-3 text-sm leading-7">{children}</p>,
              ul: ({ children }) => <ul className="mb-4 ml-6 list-disc space-y-2 text-sm">{children}</ul>,
              ol: ({ children }) => <ol className="mb-4 ml-6 list-decimal space-y-2 text-sm">{children}</ol>,
              li: ({ children }) => <li className="text-sm leading-7">{children}</li>,
              a: ({ href, children }) => (
                <a href={href} className="text-primary hover:underline" target="_blank" rel="noopener noreferrer">
                  {children}
                </a>
              ),
            }}
          >
            {markdownContent}
          </ReactMarkdown>
        </div>
      </div>
    </div>
  );
}
