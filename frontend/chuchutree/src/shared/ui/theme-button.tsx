'use client';

import { useTheme } from 'next-themes';
import { SunIcon } from 'lucide-react';
import { AppTooltip } from '@/components/custom/tooltip/AppTooltip';
import { useSyncExternalStore } from 'react';

type Theme = 'light' | 'dark' | 'system';

const nextTheme: Record<Theme, Theme> = {
  system: 'dark',
  dark: 'light',
  light: 'system',
};

// useSyncExternalStore를 위한 빈 subscribe 함수
const subscribe = () => () => {};

export default function ThemeButton() {
  const { theme, setTheme } = useTheme();

  // SSR 안전한 mounted 상태 체크
  const mounted = useSyncExternalStore(
    subscribe,
    () => true, // 클라이언트에서는 항상 true
    () => false, // 서버에서는 항상 false
  );

  const currentTheme = (theme || 'light') as Theme;

  const getThemeLabel = (theme: Theme) => {
    const labels: Record<Theme, string> = {
      system: '시스템',
      dark: '다크',
      light: '라이트',
    };
    return labels[theme];
  };

  // SSR 및 초기 hydration 중에는 플레이스홀더 렌더링
  if (!mounted) {
    return (
      <button className="hover:bg-muted flex h-8 w-full items-center rounded-sm" disabled>
        <div className="flex h-4 w-full cursor-pointer items-center justify-between p-2 text-sm">
          <SunIcon height={16} width={16} aria-hidden="true" />
          <span className="opacity-0">light</span>
        </div>
      </button>
    );
  }

  return (
    <AppTooltip content={`${getThemeLabel(nextTheme[currentTheme])} 모드로 변경`} side="right">
      <button
        className="hover:bg-muted flex h-8 w-full items-center rounded-sm"
        onClick={() => setTheme(nextTheme[currentTheme])}
        aria-label={`테마 변경: 현재 ${getThemeLabel(currentTheme)}, 클릭하여 ${getThemeLabel(nextTheme[currentTheme])} 모드로 변경`}
      >
        <div className="flex h-4 w-full cursor-pointer items-center justify-between p-2 text-sm">
          <SunIcon height={16} width={16} aria-hidden="true" />
          {currentTheme}
        </div>
      </button>
    </AppTooltip>
  );
}
