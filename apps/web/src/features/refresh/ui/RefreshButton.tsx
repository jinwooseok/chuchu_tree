import { useRefresh } from '@/entities/refresh';
import { Loader, RefreshCw } from 'lucide-react';
import { toast } from '@/lib/utils/toast';
import { AppTooltip } from '@/components/custom/tooltip/AppTooltip';

export default function RefreshButton() {
  const { mutate: refresh, isPending: isRefreshPending } = useRefresh({
    onSuccess: () => {
      toast.success('프로필이 갱신되었습니다.');
    },
    onError: () => {
      toast.error('프로필 갱신에 실패했습니다');
    },
  });

  return (
    <AppTooltip content="프로필 갱신(드래그 가능)" side="bottom">
      <button
        onClick={() => refresh()}
        disabled={isRefreshPending}
        aria-label="프로필 갱신"
        className="group active:shadow-nonee border-only-black bg-antiground hover:bg-background relative flex h-10 w-40 items-center overflow-hidden rounded-lg border-2 shadow-[4px_4px_0_0_var(--only-black)] transition-all duration-300 active:translate-x-0.75 active:translate-y-0.75"
      >
        {/* Text shadow-[4px_4px_0_0_rgb(30,41,59)] */}
        <span className="text-only-black absolute left-4 translate-x-3.75 font-semibold transition-all duration-300 group-hover:opacity-0">Refresh</span>
        {/* Icon Container */}
        <div className="bg-logo absolute right-0 flex h-full w-10 items-center justify-center transition-all duration-300 group-hover:w-full">
          {isRefreshPending ? <Loader className="text-foreground h-5 w-5 animate-spin" style={{ animationDuration: '2s' }} /> : <RefreshCw className="text-foreground h-5 w-5" />}
        </div>
      </button>
    </AppTooltip>
  );
}
