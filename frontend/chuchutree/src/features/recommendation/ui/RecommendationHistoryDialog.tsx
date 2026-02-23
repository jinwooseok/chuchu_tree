'use client';

import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { useRecommendationStore } from '@/lib/store/recommendation';
import { useCalendarStore } from '@/lib/store/calendar';
import { useCalendar, useUpdateWillSolveProblems, useUpdateRepresentativeTag } from '@/entities/calendar';
import { toast } from '@/lib/utils/toast';
import { Trash2, Ban, CheckCircle } from 'lucide-react';
import { useBanProblem, useUnbanProblem, useGetBannedProblems } from '@/entities/recommendation';
import { AppTooltip } from '@/components/custom/tooltip/AppTooltip';
import { useMemo } from 'react';
import { formatDateString } from '@/lib/utils/date';
import { getErrorCode, getErrorMessage } from '@/lib/utils/error';
import Image from 'next/image';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { TAG_INFO } from '@/shared/constants/tagSystem';

interface props {
  onClose: () => void;
}

export function RecommendationHistoryDialog({ onClose }: props) {
  const { recommendationHistory, showFilters, clearRecommendationHistory, toggleFilter, resetFilters } = useRecommendationStore();
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
    if (!bannedProblemsData) return false;
    return bannedProblemsData.bannedProblems.some((p) => p.problemId === problemId);
  };

  // Toggle problem registration (add or remove)
  const handleToggleProblem = (problemId: number, problemTags: any[]) => {
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
            if (problemTags.length > 0) {
              updateRepresentativeTag.mutate({
                date: formatDateString(selectedDate),
                problemId,
                representativeTagCode: problemTags[0].tagCode,
              });
            }
          }
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

  const formatTimestamp = (timestamp: number) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return '방금 전';
    if (diffMins < 60) return `${diffMins}분 전`;
    if (diffHours < 24) return `${diffHours}시간 전`;
    if (diffDays < 7) return `${diffDays}일 전`;

    const month = date.getMonth() + 1;
    const day = date.getDate();
    const hours = date.getHours();
    const minutes = date.getMinutes();
    return `${month}월 ${day}일 ${hours}:${minutes.toString().padStart(2, '0')}`;
  };

  const handleClearHistory = () => {
    clearRecommendationHistory();
    toast.success('추천 기록이 삭제되었습니다.');
  };

  const filters = [
    { key: 'problemNumber' as const, label: '문제번호' },
    { key: 'problemTier' as const, label: '문제티어' },
    { key: 'recommendReason' as const, label: '추천이유' },
    { key: 'algorithm' as const, label: '알고리즘' },
  ];

  // Initial state for comparison
  const initialShowFilters = {
    problemNumber: true,
    problemTier: true,
    recommendReason: true,
    algorithm: false,
  };

  // Check if current state is different from initial state
  const hasFilterChanges = JSON.stringify(showFilters) !== JSON.stringify(initialShowFilters);

  return (
    <Dialog open={true} onOpenChange={onClose}>
      <DialogContent className="flex max-h-[90vh] min-w-[50vw] flex-col">
        <DialogHeader>
          <DialogTitle>추천 기록</DialogTitle>
          <DialogDescription>과거에 추천받은 문제들을 확인할 수 있습니다.</DialogDescription>
        </DialogHeader>

        {recommendationHistory.length > 0 ? (
          <div className="min-h-0 flex-1 overflow-y-auto pr-4">
            <div className="space-y-3">
              {recommendationHistory.map((historyItem, index) => {
                return (
                  <div key={historyItem.timestamp} className="bg-innerground-hovergray/30 rounded-lg">
                    <div className="flex items-center justify-between rounded-t-lg p-3">
                      <div className="flex items-center gap-3">
                        <span className="text-sm font-medium">{formatTimestamp(historyItem.timestamp)}</span>
                        <span className="text-muted-foreground text-xs">{historyItem.problems.length}개 문제</span>
                      </div>
                    </div>

                    <div className="space-y-2 px-3 pb-3">
                      {historyItem.problems.map((problem) => {
                        const isRegistered = isProblemRegistered(problem.problemId);
                        const isBanned = isProblemBanned(problem.problemId);
                        return (
                          <div key={problem.problemId} className="flex">
                            <Button
                              className={`${isRegistered ? 'bg-primary hover:bg-primary/90' : 'bg-innerground-darkgray'} hover:bg-excluded-bg text-muted-foreground hover:text-excluded-text h-14 w-8 cursor-pointer items-center justify-center rounded-l-lg rounded-r-none text-xs`}
                              onClick={() => handleToggleProblem(problem.problemId, problem.tags)}
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
                              className="bg-innerground-hovergray/50 text-foreground hover:bg-innerground-darkgray/70 flex h-14 flex-1 cursor-pointer items-center justify-between rounded-l-none rounded-r-lg px-2 text-xs"
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
                                    {showFilters.algorithm && problem.tags.length > 0 && (
                                      <p className="line-clamp-1">{TAG_INFO[problem.tags[0].tagCode as keyof typeof TAG_INFO]?.kr ?? problem.tags[0].tagDisplayName}</p>
                                    )}
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
                  </div>
                );
              })}
            </div>
          </div>
        ) : (
          <div className="flex min-h-64 flex-1 flex-col items-center justify-center gap-2">
            <p className="text-muted-foreground text-sm">추천 기록이 없습니다.</p>
          </div>
        )}

        <div className="flex shrink-0 items-center justify-between gap-2 border-t pt-4">
          <div className="flex items-center gap-2">
            {recommendationHistory.length > 0 && (
              <Button variant="destructive" size="sm" onClick={handleClearHistory}>
                기록 전체 삭제
              </Button>
            )}
            <Popover>
              <PopoverTrigger asChild>
                <Button variant="outline" size="sm" className="relative">
                  표시 항목
                  {hasFilterChanges && <div className="bg-primary/80 absolute top-0 -right-1 h-2 w-2 rounded-full" />}
                </Button>
              </PopoverTrigger>
              <PopoverContent className="w-40 p-2">
                <div className="space-y-2">
                  {filters.map((filter) => (
                    <label key={filter.key} aria-label={filter.label} className="hover:bg-background/60 flex cursor-pointer items-center gap-2 rounded p-1">
                      <input
                        type="checkbox"
                        checked={showFilters[filter.key]}
                        onChange={() => toggleFilter(filter.key)}
                        className="checked:bg-primary checked:border-primary border-muted-foreground h-4 w-4 cursor-pointer appearance-none rounded border-2"
                      />
                      <span className="text-xs">{filter.label}</span>
                    </label>
                  ))}
                </div>
                {hasFilterChanges && (
                  <div className="mt-2 flex justify-end border-t pt-2">
                    <button onClick={resetFilters} className="text-muted-foreground hover:text-foreground text-xs underline">
                      초기화
                    </button>
                  </div>
                )}
              </PopoverContent>
            </Popover>
          </div>
          <Button variant="outline" onClick={onClose}>
            닫기
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
