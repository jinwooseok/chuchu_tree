'use client';

import { Button } from '@/components/ui/button';
import Image from 'next/image';
import { useRecommendationStore } from '@/lib/store/recommendation';
import { useCalendarStore } from '@/lib/store/calendar';
import { useUpdateWillSolveProblems } from '@/entities/calendar';
import { toast } from 'sonner';
import temp from '@/entities/recommendation/mockdata/mock_recommendation.json';

// Date to YYYY-MM-DD format
const formatDateString = (date: Date): string => {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
};

export function RecommendationAnswer() {
  const { problems, isLoading, showFilters } = useRecommendationStore();
  const { selectedDate, getWillSolveProblemsByDate } = useCalendarStore();

  const updateWillSolve = useUpdateWillSolveProblems({
    onError: (error: any) => {
      const errorMessage = error?.response?.data?.message || '문제 등록에 실패했습니다.';
      toast.error(errorMessage, {
        position: 'top-center',
      });
    },
  });

  const handleAddProblem = (problemId: number) => {
    if (!selectedDate) {
      toast.error('날짜를 먼저 선택해주세요.', {
        position: 'top-center',
      });
      return;
    }

    // Get existing will solve problems for the selected date
    const willSolveProblems = getWillSolveProblemsByDate(selectedDate);

    // Check if problem already exists
    if (willSolveProblems.some((p) => p.problemId === problemId)) {
      toast.warning('이미 등록된 문제입니다.', {
        position: 'top-center',
      });
      return;
    }

    // Add new problem to existing list
    const problemIds = [...willSolveProblems.map((p) => p.problemId), problemId];

    updateWillSolve.mutate(
      {
        date: formatDateString(selectedDate),
        problemIds,
      },
      {
        onSuccess: () => {
          toast.success(`문제 ${problemId}를 추가했습니다.`, {
            position: 'top-center',
          });
        },
      },
    );
  };

  if (isLoading) {
    return (
      <div className="flex h-full flex-col items-center justify-center gap-2 rounded-lg border-2 border-dashed p-2">
        <div className="text-muted-foreground text-sm">추천 중...</div>
      </div>
    );
  }

  // if (problems.length === 0) {
  //   return (
  //     <div className="flex h-full flex-col items-center justify-center gap-2 rounded-lg border-2 border-dashed p-2">
  //       <div className="text-muted-foreground text-sm">추천받기 버튼을 눌러주세요</div>
  //     </div>
  //   );
  // }

  return (
    <div className="flex h-full flex-col gap-2 rounded-lg border-2 border-dashed p-2">
      {problems.length === 0 ? (
        <>
          {temp.data.problems.map((problem) => (
            <div key={problem.problemId} className="flex flex-1">
              <Button
                className="bg-muted-foreground h-full flex-col items-center justify-center rounded-l-lg rounded-r-none text-xs"
                onClick={() => handleAddProblem(problem.problemId)}
                disabled={updateWillSolve.isPending}
              >
                <p>문제</p>
                <p>등록</p>
              </Button>
              <div className="bg-background text-foreground flex h-full flex-1 items-center justify-between rounded-l-none rounded-r-lg px-2 text-xs">
                <div className="flex items-center gap-2">
                  {showFilters.problemTier && (
                    <div className="flex min-w-20 items-center">
                      <Image src={`/tiers/tier_${problem.problemTierLevel}.svg`} alt={`Tier ${problem.problemTierLevel}`} width={24} height={24} className="h-6 w-6" />
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
                  {showFilters.algorithm && problem.tags.length > 0 && <p className="line-clamp-1">{problem.tags[0].tagDisplayName}</p>}
                  {showFilters.recommendReason && problem.recommandReasons.length > 0 && <p className="text-muted-foreground line-clamp-1">{problem.recommandReasons[0].reason}</p>}
                </div>
              </div>
            </div>
          ))}
        </>
      ) : (
        <>
          {problems.map((problem) => (
            <div key={problem.problemId} className="flex flex-1">
              <Button
                className="bg-muted-foreground h-full flex-col items-center justify-center rounded-l-lg rounded-r-none text-xs"
                onClick={() => handleAddProblem(problem.problemId)}
                disabled={updateWillSolve.isPending}
              >
                <p>문제</p>
                <p>등록</p>
              </Button>
              <div className="bg-background text-foreground flex h-full flex-1 items-center justify-between rounded-l-none rounded-r-lg px-2 text-xs">
                <div className="flex items-center gap-2">
                  {showFilters.problemTier && (
                    <div className="flex min-w-20 items-center">
                      <Image src={`/tiers/tier_${problem.problemTierLevel}.svg`} alt={`Tier ${problem.problemTierLevel}`} width={24} height={24} className="h-6 w-6" />
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
                  {showFilters.algorithm && problem.tags.length > 0 && <p className="line-clamp-1">{problem.tags[0].tagDisplayName}</p>}
                  {showFilters.recommendReason && problem.recommandReasons.length > 0 && <p className="text-muted-foreground line-clamp-1">{problem.recommandReasons[0].reason}</p>}
                </div>
              </div>
            </div>
          ))}
        </>
      )}
    </div>
  );
}
