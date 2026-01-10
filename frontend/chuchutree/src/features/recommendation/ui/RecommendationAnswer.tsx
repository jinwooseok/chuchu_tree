'use client';

import { Button } from '@/components/ui/button';
import Image from 'next/image';
import { useRecommendationStore } from '@/lib/store/recommendation';
import { toast } from 'sonner';

export function RecommendationAnswer() {
  const { problems, isLoading, showFilters } = useRecommendationStore();

  const handleAddProblem = (problemId: number) => {
    // TODO: Will Solve API implementation
    toast.success(`문제 ${problemId}를 추가했습니다.`, {
      position: 'top-center',
    });
  };

  if (isLoading) {
    return (
      <div className="flex h-full flex-col items-center justify-center gap-2 rounded-lg border-2 border-dashed p-2">
        <div className="text-muted-foreground text-sm">추천 중...</div>
      </div>
    );
  }

  if (problems.length === 0) {
    return (
      <div className="flex h-full flex-col items-center justify-center gap-2 rounded-lg border-2 border-dashed p-2">
        <div className="text-muted-foreground text-sm">추천받기 버튼을 눌러주세요</div>
      </div>
    );
  }

  return (
    <div className="flex h-full flex-col gap-2 rounded-lg border-2 border-dashed p-2">
      {problems.map((problem) => (
        <div key={problem.problemId} className="flex flex-1">
          <Button
            className="bg-muted-foreground h-full flex-col items-center justify-center rounded-l-lg rounded-r-none text-xs"
            onClick={() => handleAddProblem(problem.problemId)}
          >
            <p>문제</p>
            <p>등록</p>
          </Button>
          <div className="bg-background text-foreground flex h-full flex-1 items-center justify-between rounded-l-none rounded-r-lg px-2 text-xs">
            <div className="flex items-center gap-2">
              {showFilters.problemTier && (
                <div className="flex min-w-20 items-center">
                  <Image
                    src={`/tiers/tier_${problem.problemTierLevel}.svg`}
                    alt={`Tier ${problem.problemTierLevel}`}
                    width={24}
                    height={24}
                    className="h-6 w-6"
                  />
                  {showFilters.problemNumber && <p>{problem.problemId}</p>}
                </div>
              )}
              {!showFilters.problemTier && showFilters.problemNumber && (
                <div className="flex min-w-20 items-center">
                  <p>{problem.problemId}</p>
                </div>
              )}
              <p className="line-clamp-1">{problem.problemTitle}</p>
            </div>
            <div className="flex min-w-30 flex-col items-end">
              {showFilters.algorithm && problem.tags.length > 0 && (
                <p className="line-clamp-1">{problem.tags[0].tagDisplayName}</p>
              )}
              {showFilters.recommendReason && problem.recommandReasons.length > 0 && (
                <p className="text-muted-foreground line-clamp-1">
                  {problem.recommandReasons[0].reason}
                </p>
              )}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
