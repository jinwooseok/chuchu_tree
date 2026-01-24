'use client';

import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { useUser } from '@/entities/user/model/queries';
import { useBatchSolvedProblems } from '@/entities/calendar';
import { useState, useMemo } from 'react';
import { toast } from '@/lib/utils/toast';
import { ExternalLink, Loader2, RotateCcw } from 'lucide-react';

interface props {
  onClose: () => void;
}

interface ProblemData {
  problemId: number;
  solvedAt: string;
}

export function AddPrevProblemsDialog({ onClose }: props) {
  const { data: user } = useUser();
  const [htmlContent, setHtmlContent] = useState('');
  const [accumulatedProblems, setAccumulatedProblems] = useState<ProblemData[]>([]); // 누적된 문제들
  const [pasteCount, setPasteCount] = useState(0); // 붙여넣기 횟수

  const batchSolvedProblems = useBatchSolvedProblems({
    onSuccess: () => {
      toast.success(`${accumulatedProblems.length}개의 문제가 등록되었습니다.`);
      onClose();
    },
    onError: () => {
      toast.error('문제 등록에 실패했습니다. 다시 시도해주세요.');
    },
  });

  // 현재 htmlContent에서 파싱한 문제들
  const currentParsedProblems = useMemo<ProblemData[]>(() => {
    if (!htmlContent.trim()) return [];

    try {
      const parser = new DOMParser();
      const doc = parser.parseFromString(htmlContent, 'text/html');
      const rows = doc.querySelectorAll('tbody tr');
      const problemMap = new Map<number, string>(); // 중복 제거용

      rows.forEach((row) => {
        const problemLink = row.querySelector('a[href^="/problem/"]');
        const dateElement = row.querySelector('a.show-date');

        if (problemLink && dateElement) {
          const problemId = parseInt(problemLink.textContent?.trim() || '0');
          const solvedDate = dateElement.getAttribute('data-original-title') || '';

          // 중복 제거: 이미 등록되지 않은 경우만 추가
          if (!problemMap.has(problemId) && problemId > 0 && solvedDate) {
            problemMap.set(problemId, solvedDate);
          }
        }
      });

      return Array.from(problemMap.entries()).map(([problemId, solvedAt]) => ({
        problemId,
        solvedAt,
      }));
    } catch (error) {
      console.error('HTML 파싱 에러:', error);
      return [];
    }
  }, [htmlContent]);

  // HTML 추가 버튼 클릭
  const handleAddHtml = () => {
    if (currentParsedProblems.length === 0) {
      toast.error('감지된 문제가 없습니다. HTML을 다시 확인해주세요.');
      return;
    }

    // 기존 문제와 중복 제거하며 병합
    const problemMap = new Map<number, string>();

    // 기존 누적 문제 추가
    accumulatedProblems.forEach((p) => {
      problemMap.set(p.problemId, p.solvedAt);
    });

    // 새로 파싱한 문제 추가
    currentParsedProblems.forEach((p) => {
      problemMap.set(p.problemId, p.solvedAt);
    });

    const mergedProblems = Array.from(problemMap.entries()).map(([problemId, solvedAt]) => ({
      problemId,
      solvedAt,
    }));

    setAccumulatedProblems(mergedProblems);
    setPasteCount((prev) => prev + 1);
    setHtmlContent(''); // 입력 초기화
    toast.success(`${currentParsedProblems.length}개 문제 추가 (총 ${mergedProblems.length}개)`);
  };

  // 초기화
  const handleReset = () => {
    setAccumulatedProblems([]);
    setHtmlContent('');
    setPasteCount(0);
  };

  // 최종 등록
  const handleSubmit = async () => {
    if (accumulatedProblems.length === 0) {
      toast.error('등록할 문제가 없습니다.');
      return;
    }

    // 날짜별로 그룹핑
    const dateMap = new Map<string, number[]>();

    accumulatedProblems.forEach((problem) => {
      // "2025년 1월 7일 01:35:38" -> "2025-01-07" 형식으로 변환
      const dateMatch = problem.solvedAt.match(/(\d{4})년\s*(\d{1,2})월\s*(\d{1,2})일/);
      if (dateMatch) {
        const [, year, month, day] = dateMatch;
        const dateKey = `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`;

        if (!dateMap.has(dateKey)) {
          dateMap.set(dateKey, []);
        }
        dateMap.get(dateKey)!.push(problem.problemId);
      }
    });

    // BatchSolvedProblems[] 형식으로 변환
    const batchData = Array.from(dateMap.entries()).map(([date, problemIds]) => ({
      date,
      problemIds,
    }));

    batchSolvedProblems.mutate(batchData);
  };

  const bjAccountId = user?.bjAccount?.bjAccountId || '';
  const baekjoonUrl = `https://www.acmicpc.net/status?problem_id=&user_id=${bjAccountId}&language_id=-1&result_id=4`;

  return (
    <Dialog open={true} onOpenChange={onClose}>
      <DialogContent className="flex max-h-[90vh] max-w-2xl flex-col">
        <DialogHeader>
          <DialogTitle>가입 이전에 풀었던 문제 등록하기</DialogTitle>
          <DialogDescription>백준에서 HTML을 복사하여 과거 풀이 기록을 자동으로 등록할 수 있습니다.</DialogDescription>
        </DialogHeader>

        <div className="flex-1 space-y-6 overflow-y-auto py-4 pr-4">
          {/* 1단계: 백준 페이지 열기 */}
          <div className="space-y-2">
            <h3 className="font-semibold">1단계: 백준 페이지 열기</h3>
            <Button variant="outline" onClick={() => window.open(baekjoonUrl, '_blank')} className="w-full" disabled={!bjAccountId}>
              <ExternalLink className="mr-2 h-4 w-4" />
              백준 내 풀이 페이지 열기
            </Button>
          </div>

          {/* 2단계: HTML 복사하기 */}
          <div className="space-y-2">
            <h3 className="font-semibold">2단계: HTML 복사하기</h3>
            <div className="bg-innerground-hovergray/50 space-y-2 rounded-lg p-4">
              <ol className="text-muted-foreground list-inside list-decimal space-y-1 text-sm">
                <li>백준 페이지에서 Ctrl+Shift+C 누르기</li>
                <li>Ctrl+C 누르기</li>
              </ol>
              <p className="text-muted-foreground mt-2 text-xs">→ 개발자도구가 열리며 HTML이 자동 복사됩니다</p>
            </div>
          </div>

          {/* 3단계: HTML 붙여넣기 */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <h3 className="font-semibold">3단계: HTML 붙여넣기</h3>
              {accumulatedProblems.length > 0 && (
                <Button variant="outline" size="sm" onClick={handleReset}>
                  <RotateCcw className="mr-1 h-3 w-3" />
                  초기화
                </Button>
              )}
            </div>
            <div
              className="bg-innerground-hovergray/50 hover:bg-innerground-darkgray/70 border-input flex min-h-30 cursor-text items-center justify-center rounded-md border-2 border-dashed p-6 transition-colors"
              onClick={(e) => {
                const textarea = e.currentTarget.querySelector('textarea');
                textarea?.focus();
              }}
            >
              <textarea
                placeholder="여기를 클릭하고 Ctrl+V로 붙여넣기"
                value={htmlContent}
                onChange={(e) => setHtmlContent(e.target.value)}
                className="h-0 w-0 opacity-0"
                style={{ position: 'absolute' }}
              />
              {htmlContent ? (
                <div className="text-center">
                  <p className="text-foreground mb-2 text-lg font-semibold">✓ 붙여넣기 완료</p>
                  <p className="text-muted-foreground text-sm">감지된 문제: {currentParsedProblems.length}개</p>
                </div>
              ) : (
                <div className="text-center">
                  <p className="text-muted-foreground text-sm">여기를 클릭하고 Ctrl+V로 붙여넣기</p>
                  {accumulatedProblems.length > 0 && (
                    <p className="text-muted-foreground mt-1 text-xs">
                      누적된 문제: {accumulatedProblems.length}개 (페이지 {pasteCount}개)
                    </p>
                  )}
                </div>
              )}
            </div>
            {htmlContent && currentParsedProblems.length > 0 && (
              <Button variant="secondary" onClick={handleAddHtml} className="w-full">
                이 페이지 추가하기 ({currentParsedProblems.length}개)
              </Button>
            )}
          </div>

          {/* 설명 */}
          <div className="bg-innerground-hovergray/30 rounded-lg p-3">
            <p className="text-muted-foreground mb-1 text-xs">💡 이 기능은 백준 서버를 크롤링하지 않으며, 사용자가 직접 제공한 HTML만 파싱합니다.</p>
            <p className="text-muted-foreground text-xs">{`💡 여러 페이지를 붙여넣고 싶다면, 위 과정을 반복하여 "이 페이지 추가하기"를 클릭하세요.`}</p>
          </div>
        </div>

        <div className="flex shrink-0 justify-end gap-2 pt-4">
          <Button variant="outline" onClick={onClose} disabled={batchSolvedProblems.isPending}>
            닫기
          </Button>
          <Button onClick={handleSubmit} disabled={batchSolvedProblems.isPending || accumulatedProblems.length === 0}>
            {batchSolvedProblems.isPending ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                등록 중...
              </>
            ) : (
              `등록하기 (${accumulatedProblems.length}개)`
            )}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
