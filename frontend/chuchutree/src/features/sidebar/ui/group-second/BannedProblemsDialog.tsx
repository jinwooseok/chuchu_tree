'use client';

import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { useGetBannedProblems, useUnbanProblem } from '@/entities/recommendation';
import { toast } from '@/lib/utils/toast';
import Image from 'next/image';
import { X, Loader2 } from 'lucide-react';
import { TAG_INFO } from '@/shared/constants/tagSystem';

interface props {
  onClose: () => void;
}

export function BannedProblemsDialog({ onClose }: props) {
  const { data: bannedProblemsData, isLoading } = useGetBannedProblems();
  const { mutate: unbanProblem, isPending } = useUnbanProblem();

  const handleUnbanProblem = (problemId: number, problemTitle: string) => {
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
  };

  return (
    <Dialog open={true} onOpenChange={onClose}>
      <DialogContent className="flex max-h-[90vh] max-w-2xl flex-col">
        <DialogHeader>
          <DialogTitle>제외된 문제 목록</DialogTitle>
          <DialogDescription>추천에서 제외된 문제들을 확인하고 관리할 수 있습니다.</DialogDescription>
        </DialogHeader>

        {isLoading ? (
          <div className="flex min-h-64 flex-1 items-center justify-center">
            <Loader2 className="text-muted-foreground h-8 w-8 animate-spin" />
          </div>
        ) : bannedProblemsData && bannedProblemsData.bannedProblems.length > 0 ? (
          <div className="min-h-0 flex-1 overflow-y-auto pr-4">
            <div className="space-y-2">
              {bannedProblemsData.bannedProblems.map((problem) => (
                <div
                  key={problem.problemId}
                  className="bg-innerground-hovergray/50 hover:bg-innerground-darkgray/70 flex cursor-pointer items-center justify-between rounded-lg p-3 transition-colors"
                  onClick={() => window.open(`https://www.acmicpc.net/problem/${problem.problemId}`, '_blank')}
                >
                  <div className="flex flex-1 items-center gap-5">
                    <Image src={`/tiers/tier_${problem.problemTierLevel}.svg`} alt={`Tier ${problem.problemTierLevel}`} width={16} height={16} className="shrink-0" />

                    <div className="flex flex-1 flex-col gap-1">
                      <div className="flex items-center gap-2">
                        <span className="text-muted-foreground text-sm">#{problem.problemId}</span>
                        <span className="font-medium">{problem.problemTitle}</span>
                      </div>
                      {problem.tags.length > 0 && (
                        <div className="flex flex-wrap gap-1">
                          {problem.tags.map((tag) => (
                            <span key={tag.tagId} className="bg-innerground-darkgray text-muted-foreground rounded px-2 py-0.5 text-xs">
                              {TAG_INFO[tag.tagCode] ? TAG_INFO[tag.tagCode].kr : tag.tagDisplayName}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>

                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleUnbanProblem(problem.problemId, problem.problemTitle);
                    }}
                    disabled={isPending}
                    className="hover:bg-excluded-bg hover:text-excluded-text ml-2 shrink-0"
                  >
                    <X className="mr-1 h-4 w-4" />
                    제외 취소
                  </Button>
                </div>
              ))}
            </div>
          </div>
        ) : (
          <div className="flex min-h-64 flex-1 flex-col items-center justify-center gap-2">
            <p className="text-muted-foreground text-sm">제외된 문제가 없습니다.</p>
          </div>
        )}

        <div className="flex shrink-0 justify-end gap-2 pt-4">
          <Button variant="outline" onClick={onClose}>
            닫기
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
