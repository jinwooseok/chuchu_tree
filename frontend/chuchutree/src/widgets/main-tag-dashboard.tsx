import { ThemeButton } from "@/shared/ui";

export default function MainTagDashboard() {
  return (
    <div className="bg-innerground-white h-full overflow-auto p-8">
      <div className="text-center">
        <h2 className="text-2xl font-bold">태그 대시보드 영역</h2>
        <p className="text-muted-foreground mt-2">Grid 형태의 태그 카드들 (준비중)</p>
        <ThemeButton />
      </div>
    </div>
  );
}
