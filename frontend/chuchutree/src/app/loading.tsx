import { Skeleton } from '@/components/ui/skeleton';

export default function Loading() {
  return (
    <div className="bg-background flex h-screen w-screen">
      {/* AppSidebar */}
      <div className="bg-sidebar h-full w-16" />

      {/* Main Content */}
      <div className="flex h-full w-full items-center justify-center">
        <div className="flex h-[calc(100vh-16px)] w-full gap-2 overflow-hidden">
          {/* InfoSidebar */}
          <div className="bg-innerground-white flex h-full w-1/5 flex-col space-y-6 rounded-l-xl p-4">
            <Skeleton className="h-1/3 w-full rounded-lg" />
            <Skeleton className="h-1/6 w-full rounded-lg" />
            <Skeleton className="w-full flex-1 rounded-lg" />
          </div>

          {/* Main Area */}
          <div className="mr-2 flex flex-1 flex-col gap-2">
            {/* 캘린더 영역 */}
            <div className="bg-innerground-white flex flex-1 flex-col gap-2 rounded-tr-xl p-4">
              <div className="flex h-8 w-full justify-between">
                <Skeleton className="h-full w-24 rounded-lg" />
                <div className="flex h-full w-30 gap-2">
                  <Skeleton className="h-full w-1/3 rounded-lg" />
                  <Skeleton className="h-full w-1/3 rounded-lg" />
                  <Skeleton className="h-full w-1/3 rounded-lg" />
                </div>
              </div>
              <Skeleton className="w-full flex-1 rounded-lg" />
            </div>

            {/* 하단 영역 */}
            <div className="bg-innerground-white flex h-1/3 gap-2 rounded-br-xl p-6">
              <Skeleton className="h-full w-1/4 rounded-lg" />
              <Skeleton className="h-full flex-1 rounded-lg" />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
