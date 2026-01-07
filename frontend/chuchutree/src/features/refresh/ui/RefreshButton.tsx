import { useRefresh } from '@/entities/refresh';
import { Spinner } from '@/shared/ui';
import { RefreshCw } from 'lucide-react';

export default function RefreshButton() {
  const updateProblems = useRefresh();

  const handleUpdate = () => {
    updateProblems.mutate(undefined, {
      onSuccess: () => {
        alert('데이터가 업데이트되었습니다!');
      },
      onError: () => {
        alert('업데이트 실패');
      },
    });
  };

  return (
    <button
      onClick={handleUpdate}
      disabled={updateProblems.isPending}
      className="group active:shadow-nonee border-foreground bg-background hover:bg-background relative flex h-10 w-40 items-center overflow-hidden rounded-lg border-2 shadow-[4px_4px_0_0_rgb(30,41,59)] transition-all duration-300 active:translate-x-0.75 active:translate-y-0.75"
    >
      {/* Text */}
      <span className="text-foreground absolute left-4 translate-x-3.75 font-semibold transition-all duration-300 group-hover:opacity-0">Refresh</span>
      {/* Icon Container */}
      <div className="bg-logo absolute right-0 flex h-full w-10 items-center justify-center transition-all duration-300 group-hover:w-full">
        {updateProblems.isPending ? <Spinner /> : <RefreshCw className="text-foreground h-5 w-5" />}
      </div>
    </button>
  );
}
