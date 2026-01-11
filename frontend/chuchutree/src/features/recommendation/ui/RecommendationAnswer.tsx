'use client';

import { Button } from '@/components/ui/button';
import Image from 'next/image';
import { useRecommendationStore } from '@/lib/store/recommendation';
import { useCalendarStore } from '@/lib/store/calendar';
import { useUpdateWillSolveProblems } from '@/entities/calendar';
import { toast } from 'sonner';
import temp from '@/entities/recommendation/mockdata/mock_recommendation.json';
import { Trash2, CheckCircle } from 'lucide-react';
import { useBanProblem } from '@/entities/recommendation';

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
  const { mutate: banProblem, isPending } = useBanProblem();

  const updateWillSolve = useUpdateWillSolveProblems({
    onError: (error: any) => {
      const errorMessage = error?.response?.data?.message || '문제 등록에 실패했습니다.';
      toast.error(errorMessage, {
        position: 'top-center',
      });
    },
  });

  // Check if problem is already registered
  const isProblemRegistered = (problemId: number): boolean => {
    if (!selectedDate) return false;
    const willSolveProblems = getWillSolveProblemsByDate(selectedDate);
    return willSolveProblems.some((p) => p.problemId === problemId);
  };

  // Toggle problem registration (add or remove)
  const handleToggleProblem = (problemId: number) => {
    if (!selectedDate) {
      toast.error('날짜를 먼저 선택해주세요.', {
        position: 'top-center',
      });
      return;
    }

    // Get existing will solve problems for the selected date
    const willSolveProblems = getWillSolveProblemsByDate(selectedDate);
    const isRegistered = willSolveProblems.some((p) => p.problemId === problemId);

    let problemIds: number[];
    let successMessage: string;

    if (isRegistered) {
      // Remove problem from list
      problemIds = willSolveProblems.filter((p) => p.problemId !== problemId).map((p) => p.problemId);
      successMessage = `문제 ${problemId}를 제거했습니다.`;
    } else {
      // Add new problem to list
      problemIds = [...willSolveProblems.map((p) => p.problemId), problemId];
      successMessage = `문제 ${problemId}를 추가했습니다.`;
    }

    updateWillSolve.mutate(
      {
        date: formatDateString(selectedDate),
        problemIds,
      },
      {
        onSuccess: () => {
          toast.success(successMessage, {
            position: 'top-center',
          });
        },
      },
    );
  };

  const handleBanProblem = (problemId: number, problemTitle: string) => {
    banProblem(
      { problemId: problemId },
      {
        onSuccess: () => {
          toast.success(`${problemTitle}문제가 추천에서 제외됩니다.`, {
            position: 'top-center',
          });
        },
        onError: () => {
          toast.error('문제 제외에 실패했습니다.', {
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

  // 테스트시 주석처리
  if (problems.length === 0) {
    return (
      <div className="flex h-full flex-col items-center justify-center gap-2 rounded-lg border-2 border-dashed p-2">
        <div className="text-muted-foreground text-sm">추천받기 버튼을 눌러주세요</div>
      </div>
    );
  }
  return (
    <div className="flex h-full flex-col gap-2 rounded-lg border-2 border-dashed p-2">
      {problems.map((problem) => {
        const isRegistered = isProblemRegistered(problem.problemId);
        return (
          <div key={problem.problemId} className="flex flex-1">
            <Button
              className={`${isRegistered ? 'bg-primary hover:bg-primary/90' : 'bg-muted-foreground'} h-full w-8 items-center justify-center rounded-l-lg rounded-r-none text-xs`}
              onClick={() => handleToggleProblem(problem.problemId)}
              disabled={updateWillSolve.isPending}
            >
              {isRegistered ? (
                <CheckCircle className="h-5 w-5" />
              ) : (
                <div className="flex flex-col">
                  <span>문제</span>
                  <span>등록</span>
                </div>
              )}
            </Button>
            <div className="bg-background text-foreground hover:bg-innerground-darkgray/70 flex h-full flex-1 items-center justify-between rounded-l-none rounded-r-lg px-2 text-xs">
              <div className="flex items-center gap-2">
                {/* left */}
                {showFilters.problemTier && !showFilters.problemNumber && (
                  <div className="flex min-w-4 items-center gap-1">
                    <Image src={`/tiers/tier_${problem.problemTierLevel}.svg`} alt={`Tier ${problem.problemTierLevel}`} width={24} height={24} className="h-4 w-4" />
                  </div>
                )}
                {showFilters.problemTier && showFilters.problemNumber && (
                  <div className="flex min-w-20 items-center gap-1">
                    <Image src={`/tiers/tier_${problem.problemTierLevel}.svg`} alt={`Tier ${problem.problemTierLevel}`} width={24} height={24} className="h-4 w-4" />
                    <p>{problem.problemId}</p>
                  </div>
                )}
                {!showFilters.problemTier && showFilters.problemNumber && (
                  <div className="flex min-w-16 items-center">
                    <p>#{problem.problemId}</p>
                  </div>
                )}
                {/* 제목 */}
                <p className="line-clamp-2">{problem.problemTitle}</p>
              </div>
              {/* right */}
              {!showFilters.algorithm && !showFilters.recommendReason ? (
                <div className="flex min-w-6 flex-col items-end">
                  <Trash2 className="text-muted-foreground hover:text-excluded-bg h-4 w-4 cursor-pointer" onClick={() => handleBanProblem(problem.problemId, problem.problemTierName)} />
                </div>
              ) : (
                <div className="flex min-w-30 flex-col items-end">
                  <div className="flex items-center justify-center gap-1">
                    {showFilters.algorithm && problem.tags.length > 0 && <p className="line-clamp-1">{problem.tags[0].tagDisplayName}</p>}
                    <Trash2 className="text-muted-foreground hover:text-excluded-bg h-4 w-4 cursor-pointer" onClick={() => handleBanProblem(problem.problemId, problem.problemTierName)} />
                  </div>
                  {showFilters.recommendReason && problem.recommandReasons.length > 0 && <p className="text-muted-foreground line-clamp-1">{problem.recommandReasons[0].reason}</p>}
                </div>
              )}
            </div>
          </div>
        );
      })}
      {/* mock data 테스트 전용  */}
      {/* {problems.length === 0 ? (
        <>
          {temp.data.problems.map((problem) => {
            const isRegistered = isProblemRegistered(problem.problemId);
            return (
              <div key={problem.problemId} className="flex flex-1">
                <Button
                  className={`${isRegistered ? 'bg-primary hover:bg-primary/90' : 'bg-muted-foreground'} h-full w-8 items-center justify-center rounded-l-lg rounded-r-none text-xs`}
                  onClick={() => handleToggleProblem(problem.problemId)}
                  disabled={updateWillSolve.isPending}
                >
                  {isRegistered ? (
                    <CheckCircle className="h-5 w-5" />
                  ) : (
                    <div className="flex flex-col">
                      <span>문제</span>
                      <span>등록</span>
                    </div>
                  )}
                </Button>
                <div className="bg-background text-foreground hover:bg-innerground-darkgray/70 flex h-full flex-1 items-center justify-between rounded-l-none rounded-r-lg px-2 text-xs">
                  <div className="flex items-center gap-2">
                    {showFilters.problemTier && !showFilters.problemNumber && (
                      <div className="flex min-w-4 items-center gap-1">
                        <Image src={`/tiers/tier_${problem.problemTierLevel}.svg`} alt={`Tier ${problem.problemTierLevel}`} width={24} height={24} className="h-4 w-4" />
                      </div>
                    )}
                    {showFilters.problemTier && showFilters.problemNumber && (
                      <div className="flex min-w-20 items-center gap-1">
                        <Image src={`/tiers/tier_${problem.problemTierLevel}.svg`} alt={`Tier ${problem.problemTierLevel}`} width={24} height={24} className="h-4 w-4" />
                        <p>{problem.problemId}</p>
                      </div>
                    )}
                    {!showFilters.problemTier && showFilters.problemNumber && (
                      <div className="flex min-w-16 items-center">
                        <p>#{problem.problemId}</p>
                      </div>
                    )}
                    <p className="line-clamp-2">{problem.problemTitle}</p>
                  </div>
                  {!showFilters.algorithm && !showFilters.recommendReason ? (
                    <div className="flex min-w-6 flex-col items-end">
                      <Trash2 className="text-muted-foreground hover:text-excluded-bg h-4 w-4 cursor-pointer" onClick={() => handleBanProblem(problem.problemId, problem.problemTierName)} />
                    </div>
                  ) : (
                    <div className="flex min-w-30 flex-col items-end">
                      <div className="flex items-center justify-center gap-1">
                        {showFilters.algorithm && problem.tags.length > 0 && <p className="line-clamp-1">{problem.tags[0].tagDisplayName}</p>}
                        <Trash2 className="text-muted-foreground hover:text-excluded-bg h-4 w-4 cursor-pointer" onClick={() => handleBanProblem(problem.problemId, problem.problemTierName)} />
                      </div>
                      {showFilters.recommendReason && problem.recommandReasons.length > 0 && <p className="text-muted-foreground line-clamp-1">{problem.recommandReasons[0].reason}</p>}
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </>
      ) : (
        <>
          {problems.map((problem) => {
            const isRegistered = isProblemRegistered(problem.problemId);
            return (
              <div key={problem.problemId} className="flex flex-1">
                <Button
                  className={`${isRegistered ? 'bg-primary hover:bg-primary/90' : 'bg-muted-foreground'} h-full w-8 items-center justify-center rounded-l-lg rounded-r-none text-xs`}
                  onClick={() => handleToggleProblem(problem.problemId)}
                  disabled={updateWillSolve.isPending}
                >
                  {isRegistered ? (
                    <CheckCircle className="h-5 w-5" />
                  ) : (
                    <div className="flex flex-col">
                      <span>문제</span>
                      <span>등록</span>
                    </div>
                  )}
                </Button>
                <div className="bg-background text-foreground hover:bg-innerground-darkgray/70 flex h-full flex-1 items-center justify-between rounded-l-none rounded-r-lg px-2 text-xs">
                  <div className="flex items-center gap-2">
                    {showFilters.problemTier && !showFilters.problemNumber && (
                      <div className="flex min-w-4 items-center gap-1">
                        <Image src={`/tiers/tier_${problem.problemTierLevel}.svg`} alt={`Tier ${problem.problemTierLevel}`} width={24} height={24} className="h-4 w-4" />
                      </div>
                    )}
                    {showFilters.problemTier && showFilters.problemNumber && (
                      <div className="flex min-w-20 items-center gap-1">
                        <Image src={`/tiers/tier_${problem.problemTierLevel}.svg`} alt={`Tier ${problem.problemTierLevel}`} width={24} height={24} className="h-4 w-4" />
                        <p>{problem.problemId}</p>
                      </div>
                    )}
                    {!showFilters.problemTier && showFilters.problemNumber && (
                      <div className="flex min-w-16 items-center">
                        <p>#{problem.problemId}</p>
                      </div>
                    )}
                    <p className="line-clamp-2">{problem.problemTitle}</p>
                  </div>
                  {!showFilters.algorithm && !showFilters.recommendReason ? (
                    <div className="flex min-w-6 flex-col items-end">
                      <Trash2 className="text-muted-foreground hover:text-excluded-bg h-4 w-4 cursor-pointer" onClick={() => handleBanProblem(problem.problemId, problem.problemTierName)} />
                    </div>
                  ) : (
                    <div className="flex min-w-30 flex-col items-end">
                      <div className="flex items-center justify-center gap-1">
                        {showFilters.algorithm && problem.tags.length > 0 && <p className="line-clamp-1">{problem.tags[0].tagDisplayName}</p>}
                        <Trash2 className="text-muted-foreground hover:text-excluded-bg h-4 w-4 cursor-pointer" onClick={() => handleBanProblem(problem.problemId, problem.problemTierName)} />
                      </div>
                      {showFilters.recommendReason && problem.recommandReasons.length > 0 && <p className="text-muted-foreground line-clamp-1">{problem.recommandReasons[0].reason}</p>}
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </>
      )} */}
    </div>
  );
}
