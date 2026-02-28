

export function StudyDashboard({ studyInfo }: { studyInfo: string }) {
  if (!studyInfo) {
    return (
      <div className="flex h-full w-full items-center justify-center">
        <p className="text-muted-foreground">로딩 중...</p>
      </div>
    );
  }

  return (
    <div className="hide-scrollbar flex h-full w-full overflow-y-auto">
      <div className="mx-auto grid w-fit grid-cols-1 content-start gap-x-4 gap-y-8 lg:grid-cols-2 xl:grid-cols-3">
        <h1>{studyInfo}</h1>
      </div>
    </div>
  );
}
