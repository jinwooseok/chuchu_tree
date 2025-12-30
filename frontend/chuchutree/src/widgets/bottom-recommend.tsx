import { ThemeButton } from '@/shared/ui';

export default function BottomRecommend() {
  return (
    <div className="bg-card flex h-full items-center justify-center border-t p-4">
      <div className="text-center">
        <h3 className="text-lg font-semibold">문제 추천</h3>
        <p className="text-muted-foreground text-sm">문제 추천 기능 (준비중)</p>
        <ThemeButton />
      </div>
    </div>
  );
}
