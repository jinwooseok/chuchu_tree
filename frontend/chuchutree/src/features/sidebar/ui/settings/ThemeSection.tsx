'use client';

import { useSyncExternalStore } from 'react';
import { useTheme } from 'next-themes';
import { Sun } from 'lucide-react';
import { Button } from '@/components/ui/button';

type Theme = 'system' | 'dark' | 'light';

const nextTheme: Record<Theme, Theme> = {
  system: 'dark',
  dark: 'light',
  light: 'system',
};

const themeLabels: Record<Theme, string> = {
  system: '시스템',
  dark: '다크',
  light: '라이트',
};

export default function ThemeSection() {
  const { theme, setTheme } = useTheme();
  const mounted = useSyncExternalStore(
    () => () => {},
    () => true,
    () => false
  );

  if (!mounted) {
    return (
      <div className="space-y-3">
        <div>
          <h3 className="text-sm font-semibold">테마</h3>
          <p className="text-muted-foreground text-xs">애플리케이션 테마를 변경합니다.</p>
        </div>
        <div className="flex items-center justify-between rounded-lg border p-4">
          <div className="flex items-center gap-3">
            <Sun className="h-5 w-5" />
            <div>
              <div className="text-sm font-medium">현재 테마</div>
              <div className="text-muted-foreground text-xs">로딩 중...</div>
            </div>
          </div>
          <Button variant="outline" disabled>
            변경
          </Button>
        </div>
      </div>
    );
  }

  const currentTheme = (theme || 'light') as Theme;
  const next = nextTheme[currentTheme];

  const handleThemeToggle = () => {
    setTheme(next);
  };

  return (
    <div className="space-y-3">
      <div>
        <h3 className="text-sm font-semibold">테마</h3>
        <p className="text-muted-foreground text-xs">애플리케이션 테마를 변경합니다.</p>
      </div>

      <div className="flex items-center justify-between rounded-lg border p-4">
        <div className="flex items-center gap-3">
          <Sun className="h-5 w-5" />
          <div>
            <div className="text-sm font-medium">현재 테마</div>
            <div className="text-muted-foreground text-xs">{themeLabels[currentTheme]} 모드</div>
          </div>
        </div>
        <Button variant="outline" onClick={handleThemeToggle}>
          {themeLabels[next]}로 변경
        </Button>
      </div>
    </div>
  );
}
