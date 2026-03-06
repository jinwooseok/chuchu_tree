'use client';

import { useState } from 'react';
import Image from 'next/image';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { ChevronDown } from 'lucide-react';
import { useGetStudyRecommendation, StudyRecommendedProblem, StudyRecommendMemberSolveInfo } from '@/entities/study';
import { StudyDetail } from '@/entities/study';
import { TAG_INFO } from '@/shared/constants/tagSystem';

interface StudyRecommendSectionProps {
  studyDetail: StudyDetail;
  currentUserAccountId: number;
}

function MemberSolveInfoBadge({ info }: { info: StudyRecommendMemberSolveInfo }) {
  return (
    <span
      className={`inline-flex items-center rounded px-1 py-0.5 text-xs font-medium ${
        info.solved ? 'bg-primary/20 text-primary' : 'bg-muted-foreground/10 text-muted-foreground'
      }`}
      title={info.bjAccountId}
    >
      {info.bjAccountId}
      {info.solved ? ' ✓' : ' ✗'}
    </span>
  );
}

function StudyRecommendProblemCard({ problem }: { problem: StudyRecommendedProblem }) {
  const firstTag = problem.tags[0];
  const tagName = firstTag ? (TAG_INFO[firstTag.tagCode as keyof typeof TAG_INFO]?.kr ?? firstTag.tagDisplayName) : null;

  return (
    <div
      className="bg-innerground-hovergray/50 hover:bg-innerground-darkgray/70 flex cursor-pointer flex-col gap-1 rounded-lg p-2 text-xs transition-colors"
      onClick={() => window.open(`https://www.acmicpc.net/problem/${problem.problemId}`, '_blank')}
    >
      <div className="flex items-center gap-2">
        <Image src={`/tiers/tier_${problem.problemTierLevel}.svg`} alt={`Tier ${problem.problemTierLevel}`} width={16} height={16} />
        <span className="text-muted-foreground">#{problem.problemId}</span>
        <span className="line-clamp-1 flex-1 font-medium">{problem.problemTitle}</span>
        {tagName && <span className="text-muted-foreground shrink-0">{tagName}</span>}
      </div>
      {problem.recommandReasons.length > 0 && (
        <p className="text-muted-foreground line-clamp-1">{problem.recommandReasons[0].reason}</p>
      )}
      {problem.studyMemberSolveInfo.length > 0 && (
        <div className="flex flex-wrap gap-1">
          {problem.studyMemberSolveInfo.map((info) => (
            <MemberSolveInfoBadge key={info.userAccountId} info={info} />
          ))}
        </div>
      )}
    </div>
  );
}

export function StudyRecommendSection({ studyDetail, currentUserAccountId }: StudyRecommendSectionProps) {
  const [targetMemberId, setTargetMemberId] = useState<number>(currentUserAccountId);
  const [recommendAllUnsolved, setRecommendAllUnsolved] = useState(false);
  const [count, setCount] = useState(3);
  const [isCountPopoverOpen, setIsCountPopoverOpen] = useState(false);
  const [result, setResult] = useState<StudyRecommendedProblem[]>([]);

  const { mutate: getRecommendation, isPending } = useGetStudyRecommendation({
    onSuccess: () => {},
    onError: () => {},
  });

  const handleRecommend = () => {
    getRecommendation(
      {
        study_id: studyDetail.studyId,
        target_user_account_id: targetMemberId,
        recommend_all_unsolved: recommendAllUnsolved,
        count,
      },
      {
        onSuccess: (data) => {
          setResult(data.problems);
        },
      },
    );
  };

  const selectedMember = studyDetail.members.find((m) => m.userAccountId === targetMemberId);
  const selectedMemberLabel = selectedMember
    ? selectedMember.userAccountId === currentUserAccountId
      ? `${selectedMember.bjAccountId} (나)`
      : selectedMember.bjAccountId
    : '멤버 선택';

  return (
    <div className="flex w-full gap-2">
      {/* 왼쪽: 컨트롤 패널 */}
      <div className="flex w-52 shrink-0 flex-col gap-2 rounded-lg border-2 border-dashed p-2">
        <div className="text-muted-foreground cursor-default text-xs font-semibold">문제 추천</div>

        {/* 멤버 선택 */}
        <Select
          value={String(targetMemberId)}
          onValueChange={(val) => setTargetMemberId(Number(val))}
        >
          <SelectTrigger className="h-7 w-full text-xs" aria-label="기준 멤버 선택">
            <SelectValue placeholder="멤버 선택">
              <span className="line-clamp-1">{selectedMemberLabel}</span>
            </SelectValue>
          </SelectTrigger>
          <SelectContent>
            {studyDetail.members.map((member) => (
              <SelectItem key={member.userAccountId} value={String(member.userAccountId)} className="text-xs">
                {member.bjAccountId}
                {member.userAccountId === currentUserAccountId ? ' (나)' : ''}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        {/* 미풀이 전체 기반 체크박스 */}
        <label className="hover:bg-background/60 flex cursor-pointer items-center gap-2 rounded px-1">
          <input
            type="checkbox"
            checked={recommendAllUnsolved}
            onChange={(e) => setRecommendAllUnsolved(e.target.checked)}
            className="checked:bg-primary checked:border-primary border-muted-foreground h-4 w-4 cursor-pointer appearance-none rounded border-2"
          />
          <span className="text-xs">미풀이 전체 기반</span>
        </label>

        {/* 추천 문제수 */}
        <div className="flex items-center justify-between px-1 text-xs">
          <span className="text-muted-foreground cursor-default">추천 문제수</span>
          <Popover open={isCountPopoverOpen} onOpenChange={setIsCountPopoverOpen}>
            <PopoverTrigger asChild>
              <Button aria-label="문제수 선택" variant="outline" className="h-6 w-8 cursor-pointer text-xs">
                {count}
                <ChevronDown className="ml-0.5 h-3 w-3" />
              </Button>
            </PopoverTrigger>
            <PopoverContent className="w-16 p-2">
              <div className="space-y-2">
                {[1, 2, 3, 4, 5, 6].map((cnt) => (
                  <label key={cnt} className="hover:bg-background/60 flex cursor-pointer items-center gap-2 rounded p-1">
                    <input
                      type="checkbox"
                      checked={count === cnt}
                      onChange={() => {
                        setCount(cnt);
                        setIsCountPopoverOpen(false);
                      }}
                      className="checked:bg-primary checked:border-primary border-muted-foreground h-4 w-4 cursor-pointer appearance-none rounded border-2"
                    />
                    <span className="text-xs">{cnt}</span>
                  </label>
                ))}
              </div>
            </PopoverContent>
          </Popover>
        </div>

        {/* 추천받기 버튼 */}
        <Button
          aria-label="스터디 문제 추천받기"
          className="flex-1 cursor-pointer"
          onClick={handleRecommend}
          disabled={isPending}
        >
          {isPending ? '추천 중...' : '추천 받기'}
        </Button>
      </div>

      {/* 오른쪽: 결과 영역 */}
      <div className="flex flex-1 flex-col gap-1 rounded-lg border-2 border-dashed p-2">
        {isPending ? (
          <div className="flex h-full items-center justify-center">
            <span className="text-muted-foreground text-sm">추천 중...</span>
          </div>
        ) : result.length === 0 ? (
          <div className="flex h-full items-center justify-center">
            <span className="text-muted-foreground text-sm">추천받기 버튼을 눌러주세요</span>
          </div>
        ) : (
          result.map((problem) => (
            <StudyRecommendProblemCard key={problem.problemId} problem={problem} />
          ))
        )}
      </div>
    </div>
  );
}
