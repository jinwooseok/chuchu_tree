import { useSetTheme, useTheme, type Theme } from '@/lib/store/theme';
import { SunIcon } from 'lucide-react';

const THEMES: Theme[] = ['system', 'dark', 'light'];
const nextTheme: Record<Theme, Theme> = {
  system: 'dark',
  dark: 'light',
  light: 'system',
};

export default function ThemeButton() {
  const currentTheme = useTheme();
  const setTheme = useSetTheme();

  return (
    <button className="hover:bg-muted flex h-8 w-full items-center rounded-sm" onClick={() => setTheme(nextTheme[currentTheme])}>
      <div className="flex h-4 w-full cursor-pointer items-center justify-between p-2 text-sm">
        <SunIcon height={16} width={16} />
        {currentTheme}
      </div>
    </button>
  );
}
