'use client';

import { Button } from '@/components/ui/button';
import Image from 'next/image';
import { useRecommendationStore } from '@/lib/store/recommendation';
import { useCalendarStore } from '@/lib/store/calendar';
import { useUpdateWillSolveProblems, useUpdateRepresentativeTag, Calendar } from '@/entities/calendar';
import { toast } from '@/lib/utils/toast';
import { Trash2, CheckCircle, Ban } from 'lucide-react';
import { useBanProblem, useUnbanProblem, BannedProblems } from '@/entities/recommendation';
import { AppTooltip } from '@/components/custom/tooltip/AppTooltip';
import { useMemo } from 'react';
import { formatDateString } from '@/lib/utils/date';
import { getErrorCode, getErrorMessage } from '@/lib/utils/error';

export function RecommendationAnswer({ calendarData, bannedListData, isLanding = false }: { calendarData?: Calendar; bannedListData?: BannedProblems; isLanding?: boolean }) {
  const { problems, isLoading, showFilters } = useRecommendationStore();
  const { selectedDate } = useCalendarStore();

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
      const errorCode = getErrorCode(error);
      const errorMessage = errorCode === 'ALREADY_SOLVED_PROBLEM' ? getErrorMessage(error) : '문제 추가에 실패했습니다.';
      toast.error(errorMessage);
    },
  });

  const updateRepresentativeTag = useUpdateRepresentativeTag();

  // Check if problem is already registered
  const isProblemRegistered = (problemId: number): boolean => {
    if (!selectedDate) return false;
    return willSolveProblems.some((p) => p.problemId === problemId);
  };

  // Check if problem is banned
  const isProblemBanned = (problemId: number): boolean => {
    if (!bannedListData) return false;
    return bannedListData.bannedProblems.some((p) => p.problemId === problemId);
  };

  // Toggle problem registration (add or remove)
  const handleToggleProblem = (problemId: number) => {
    if (isLanding) {
      toast.info('로그인 후 이용해보세요');
      return;
    }
    if (!selectedDate) {
      toast.error('날짜를 먼저 선택해주세요.');
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
          toast.success(successMessage);

          // 문제 추가 시에만 대표 태그 자동 설정
          if (!isRegistered) {
            const problem = problems.find((p) => p.problemId === problemId);
            if (problem && problem.tags.length > 0) {
              updateRepresentativeTag.mutate({
                date: formatDateString(selectedDate),
                problemId,
                representativeTagCode: problem.tags[0].tagCode,
              });
            }
          }
        },
      },
    );
  };

  const handleToggleBanProblem = (problemId: number, problemTitle: string) => {
    if (isLanding) {
      toast.info('로그인 후 이용해보세요');
      return;
    }
    const isBanned = isProblemBanned(problemId);

    if (isBanned) {
      // Unban problem
      unbanProblem(
        { problemId },
        {
          onSuccess: () => {
            toast.success(`${problemTitle} 문제가 추천에 포함됩니다.`);
          },
          onError: () => {
            toast.error('문제 제외 취소에 실패했습니다.');
          },
        },
      );
    } else {
      // Ban problem
      banProblem(
        { problemId },
        {
          onSuccess: () => {
            toast.success(`${problemTitle} 문제가 추천에서 제외됩니다.`);
          },
          onError: () => {
            toast.error('문제 제외에 실패했습니다.');
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
  const totalSlots = 3;
  const emptySlots = problems.length < totalSlots ? totalSlots - problems.length : 0;

  return (
    <div className="ml-1 h-full w-full flex-1 rounded-lg border-2 border-dashed p-2">
      <div className={`flex h-full flex-col gap-1 overflow-x-hidden ${problems.length <= 3 ? 'overflow-y-hidden' : 'overflow-y-scroll'}`}>
        {problems.map((problem) => {
          const isRegistered = isProblemRegistered(problem.problemId);
          const isBanned = isProblemBanned(problem.problemId);
          return (
            <div key={problem.problemId} className="mr-2 flex h-full">
              <Button
                className={`${isRegistered ? 'bg-primary hover:bg-primary/90' : 'bg-innerground-darkgray'} hover:bg-excluded-bg text-muted-foreground hover:text-excluded-text ${problems.length <= 3 ? 'h-full' : 'h-14'} w-8 cursor-pointer items-center justify-center rounded-l-lg rounded-r-none text-xs`}
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
        {Array.from({ length: emptySlots }).map((_, index) => (
          <div key={`empty-${index}`} className="group hover:bg-innerground-darkgray/70 mr-2 flex h-full rounded-lg">
            <div className="bg-innerground-hovergray/50 w-8 rounded-l-lg rounded-r-none" />
            <div className="bg-innerground-hovergray/50 text-muted-foreground flex h-full flex-1 cursor-default items-center justify-center rounded-l-none rounded-r-lg text-xs">
              필터를 조정하면 더 많은 문제를 추천받을 수 있습니다
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
