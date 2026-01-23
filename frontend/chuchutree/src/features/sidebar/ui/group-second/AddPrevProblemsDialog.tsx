'use client';

import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { useUser } from '@/entities/user/model/queries';
import { useState, useMemo } from 'react';
import { toast } from '@/lib/utils/toast';
import { ExternalLink, Loader2 } from 'lucide-react';

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
  const [isSubmitting, setIsSubmitting] = useState(false);

  // HTML 파싱 및 중복 제거 로직
  const parsedProblems = useMemo<ProblemData[]>(() => {
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

  const handleSubmit = async () => {
    if (parsedProblems.length === 0) {
      toast.error('감지된 문제가 없습니다. HTML을 다시 확인해주세요.');
      return;
    }

    setIsSubmitting(true);

    try {
      // TODO: API 연결 (추후 구현 예정)
      // await addPrevProblems({ problems: parsedProblems });

      // 임시: 성공 메시지
      console.log('등록할 문제들:', parsedProblems);
      toast.success(`${parsedProblems.length}개의 문제가 등록되었습니다.`);
      onClose();
    } catch (error) {
      toast.error('문제 등록에 실패했습니다. 다시 시도해주세요.');
      console.error(error);
    } finally {
      setIsSubmitting(false);
    }
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
            <h3 className="font-semibold">3단계: HTML 붙여넣기</h3>
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
                  <p className="text-muted-foreground text-sm">감지된 문제: {parsedProblems.length}개</p>
                </div>
              ) : (
                <div className="text-center">
                  <p className="text-muted-foreground text-sm">여기를 클릭하고 Ctrl+V로 붙여넣기</p>
                </div>
              )}
            </div>
          </div>

          {/* 설명 */}
          <div className="bg-innerground-hovergray/30 rounded-lg p-3">
            <p className="text-muted-foreground text-xs">💡 이 기능은 백준 서버를 크롤링하지 않으며, 사용자가 직접 제공한 HTML만 파싱합니다.</p>
          </div>
        </div>

        <div className="flex shrink-0 justify-end gap-2 pt-4">
          <Button variant="outline" onClick={onClose} disabled={isSubmitting}>
            닫기
          </Button>
          <Button onClick={handleSubmit} disabled={isSubmitting || parsedProblems.length === 0}>
            {isSubmitting ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                등록 중...
              </>
            ) : (
              '등록하기'
            )}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
