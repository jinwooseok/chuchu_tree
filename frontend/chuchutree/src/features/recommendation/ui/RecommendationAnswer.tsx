'use client';

import { Button } from '@/components/ui/button';
import Image from 'next/image';
import { useRecommendationStore } from '@/lib/store/recommendation';
import { useCalendarStore } from '@/lib/store/calendar';
import { useCalendar, useUpdateWillSolveProblems } from '@/entities/calendar';
import { toast } from 'sonner';
import { Trash2, CheckCircle, Ban } from 'lucide-react';
import { useBanProblem, useUnbanProblem, useGetBannedProblems } from '@/entities/recommendation';
import { AppTooltip } from '@/components/custom/tooltip/AppTooltip';
import { useMemo } from 'react';

// Date to YYYY-MM-DD format
const formatDateString = (date: Date): string => {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
};

export function RecommendationAnswer() {
  const { problems, isLoading, showFilters } = useRecommendationStore();
  const { selectedDate } = useCalendarStore();
  // 현재 선택된 날짜의 년/월로 calendar 데이터 fetch
  const year = selectedDate?.getFullYear() || new Date().getFullYear();
  const month = (selectedDate?.getMonth() || new Date().getMonth()) + 1;
  const { data: calendarData } = useCalendar(year, month);
  const { data: bannedProblemsData } = useGetBannedProblems();
  const { mutate: banProblem, isPending: isBanPending } = useBanProblem();
  const { mutate: unbanProblem, isPending: isUnbanPending } = useUnbanProblem();

  const willSolveProblems = useMemo(() => {
    if (!calendarData || !selectedDate) return [];
    const dateString = formatDateString(selectedDate);
    const dayData = calendarData.monthlyData.find((d) => d.targetDate === dateString);
    return dayData?.willSolveProblems || [];
  }, [calendarData, selectedDate]);

  const updateWillSolve = useUpdateWillSolveProblems({
    onError: (error) => {
      const errorCode = error?.response?.data?.error?.code;
      const errorMessage = errorCode === 'ALREADY_SOLVED_PROBLEM' ? error?.response?.data?.error?.message : '문제 추가에 실패했습니다.';
      toast.error(errorMessage, {
        position: 'top-center',
      });
    },
  });

  // Check if problem is already registered
  const isProblemRegistered = (problemId: number): boolean => {
    if (!selectedDate) return false;
    return willSolveProblems.some((p) => p.problemId === problemId);
  };

  // Check if problem is banned
  const isProblemBanned = (problemId: number): boolean => {
    if (!bannedProblemsData) return false;
    return bannedProblemsData.bannedProblems.some((p) => p.problemId === problemId);
  };

  // Toggle problem registration (add or remove)
  const handleToggleProblem = (problemId: number) => {
    if (!selectedDate) {
      toast.error('날짜를 먼저 선택해주세요.', {
        position: 'top-center',
      });
      return;
    }

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

  const handleToggleBanProblem = (problemId: number, problemTitle: string) => {
    const isBanned = isProblemBanned(problemId);

    if (isBanned) {
      // Unban problem
      unbanProblem(
        { problemId },
        {
          onSuccess: () => {
            toast.success(`${problemTitle} 문제가 추천에 포함됩니다.`, {
              position: 'top-center',
            });
          },
          onError: () => {
            toast.error('문제 제외 취소에 실패했습니다.', {
              position: 'top-center',
            });
          },
        },
      );
    } else {
      // Ban problem
      banProblem(
        { problemId },
        {
          onSuccess: () => {
            toast.success(`${problemTitle} 문제가 추천에서 제외됩니다.`, {
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
    }
  };

  if (isLoading) {
    return (
      <div className="ml-1 flex h-full w-full flex-col items-center justify-center gap-2 rounded-lg border-2 border-dashed p-2">
        <div className="text-muted-foreground text-sm">추천 중...</div>
      </div>
    );
  }

  // 테스트시 주석처리
  if (problems.length === 0) {
    return (
      <div
        className="ml-2 flex h-full flex-1 flex-col items-center justify-center gap-2 rounded-lg border-2 border-dashed p-2"
        aria-label="추천 결과 영역(추천결과가 없습니다. 추천받기 버튼을 눌러주세요)"
      >
        <div className="text-muted-foreground text-sm">추천받기 버튼을 눌러주세요</div>
      </div>
    );
  }
  return (
    <div className="ml-1 flex h-full flex-1 flex-col gap-2 rounded-lg border-2 border-dashed p-2">
      {problems.map((problem) => {
        const isRegistered = isProblemRegistered(problem.problemId);
        const isBanned = isProblemBanned(problem.problemId);
        return (
          <div key={problem.problemId} className="flex flex-1">
            <Button
              className={`${isRegistered ? 'bg-primary hover:bg-primary/90' : 'bg-innerground-darkgray'} hover:bg-excluded-bg text-muted-foreground hover:text-excluded-text h-full w-8 cursor-pointer items-center justify-center rounded-l-lg rounded-r-none text-xs`}
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
            <div
              className="bg-innerground-hovergray/50 text-foreground hover:bg-innerground-darkgray/70 flex h-full flex-1 cursor-pointer items-center justify-between rounded-l-none rounded-r-lg px-2 text-xs"
              onClick={() => window.open(`https://www.acmicpc.net/problem/${problem.problemId}`, '_blank')}
            >
              <div className="flex items-center gap-2">
                {showFilters.problemTier && !showFilters.problemNumber && (
                  <div className="flex min-w-4 items-center gap-1">
                    <Image src={`/tiers/tier_${problem.problemTierLevel}.svg`} alt={`Tier ${problem.problemTierLevel}`} width={16} height={16} />
                  </div>
                )}
                {showFilters.problemTier && showFilters.problemNumber && (
                  <div className="flex min-w-20 items-center gap-1">
                    <Image src={`/tiers/tier_${problem.problemTierLevel}.svg`} alt={`Tier ${problem.problemTierLevel}`} width={16} height={16} />
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
                  <AppTooltip content={isBanned ? '문제 추천에 포함' : '문제 추천에서 제외'} side="left">
                    <div
                      aria-label={isBanned ? '문제 추천에 포함' : '문제 추천에서 제외'}
                      role="button"
                      tabIndex={0}
                      onClick={(e) => {
                        e.stopPropagation();
                        handleToggleBanProblem(problem.problemId, problem.problemTitle);
                      }}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter') {
                          e.stopPropagation();
                          handleToggleBanProblem(problem.problemId, problem.problemTitle);
                        }
                      }}
                    >
                      {isBanned ? (
                        <Ban className="text-excluded-bg hover:text-excluded-text h-4 w-4 cursor-pointer" />
                      ) : (
                        <Trash2 className="text-muted-foreground hover:text-excluded-bg h-4 w-4 cursor-pointer" />
                      )}
                    </div>
                  </AppTooltip>
                </div>
              ) : (
                <div className="flex min-w-30 flex-col items-end">
                  <div className="flex items-center justify-center gap-1">
                    {showFilters.algorithm && problem.tags.length > 0 && <p className="line-clamp-1">{problem.tags[0].tagDisplayName}</p>}
                    <AppTooltip content={isBanned ? '문제 추천에 포함' : '문제 추천에서 제외'} side="left">
                      <div
                        aria-label={isBanned ? '문제 추천에 포함' : '문제 추천에서 제외'}
                        role="button"
                        tabIndex={0}
                        onClick={(e) => {
                          e.stopPropagation();
                          handleToggleBanProblem(problem.problemId, problem.problemTitle);
                        }}
                        onKeyDown={(e) => {
                          if (e.key === 'Enter') {
                            e.stopPropagation();
                            handleToggleBanProblem(problem.problemId, problem.problemTitle);
                          }
                        }}
                      >
                        {isBanned ? (
                          <Ban className="text-excluded-bg hover:text-excluded-text h-4 w-4 cursor-pointer" />
                        ) : (
                          <Trash2 className="text-muted-foreground hover:text-excluded-bg h-4 w-4 cursor-pointer" />
                        )}
                      </div>
                    </AppTooltip>
                  </div>
                  {showFilters.recommendReason && problem.recommandReasons.length > 0 && (
                    <p className="text-muted-foreground line-clamp-1">
                      {showFilters.algorithm
                        ? problem.recommandReasons[0].reason
                        : problem.recommandReasons[0].reason
                            .replace(/'[^']+'/g, '')
                            .replace(/\s+/g, ' ')
                            .trim()}
                    </p>
                  )}
                </div>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}
