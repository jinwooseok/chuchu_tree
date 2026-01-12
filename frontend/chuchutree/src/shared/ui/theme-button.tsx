import { useSetTheme, useTheme, type Theme } from '@/lib/store/theme';
import { SunIcon } from 'lucide-react';
import { AppTooltip } from '@/components/custom/tooltip/AppTooltip';

const THEMES: Theme[] = ['system', 'dark', 'light'];
const nextTheme: Record<Theme, Theme> = {
  system: 'dark',
  dark: 'light',
  light: 'system',
};

export default function ThemeButton() {
  const currentTheme = useTheme();
  const setTheme = useSetTheme();

  const getThemeLabel = (theme: Theme) => {
    const labels: Record<Theme, string> = {
      system: '시스템',
      dark: '다크',
      light: '라이트',
    };
    return labels[theme];
  };

  return (
    <AppTooltip content={`${getThemeLabel(nextTheme[currentTheme])} 모드로 변경`} side="right">
      <button className="hover:bg-muted flex h-8 w-full items-center rounded-sm" onClick={() => setTheme(nextTheme[currentTheme])} aria-label={`테마 변경: 현재 ${getThemeLabel(currentTheme)}, 클릭하여 ${getThemeLabel(nextTheme[currentTheme])} 모드로 변경`}>
        <div className="flex h-4 w-full cursor-pointer items-center justify-between p-2 text-sm">
          <SunIcon height={16} width={16} aria-hidden="true" />
          {currentTheme}
        </div>
      </button>
    </AppTooltip>
  );
}
