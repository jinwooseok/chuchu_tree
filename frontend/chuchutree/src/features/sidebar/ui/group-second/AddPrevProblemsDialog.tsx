'use client';

import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { useUser } from '@/entities/user/model/queries';
import { useBatchSolvedProblems } from '@/entities/calendar';
import { useState, useMemo, useEffect } from 'react';
import { toast } from '@/lib/utils/toast';
import { ExternalLink, Loader2, RotateCcw, HelpCircle, FileText, X } from 'lucide-react';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion';
import { Carousel, CarouselContent, CarouselItem, CarouselNext, CarouselPrevious } from '@/components/ui/carousel';
import Image from 'next/image';

interface props {
  onClose: () => void;
}

interface ProblemData {
  problemId: number;
  solvedAt: string;
}

interface PageInfo {
  pageNum: number;
  count: number; // 실제 추가된 개수 (중복 제외)
  duplicateCount: number; // 중복된 개수
  problemIds: number[]; // 이 페이지에서 추가된 문제 ID들
}

export function AddPrevProblemsDialog({ onClose }: props) {
  const { data: user } = useUser();
  const [htmlContent, setHtmlContent] = useState('');
  const [accumulatedProblems, setAccumulatedProblems] = useState<ProblemData[]>([]); // 누적된 문제들
  const [pageInfos, setPageInfos] = useState<PageInfo[]>([]); // 페이지별 정보

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

  // 자동 추가 - htmlContent가 변경되고 파싱된 문제가 있으면 자동으로 추가
  useEffect(() => {
    if (htmlContent && currentParsedProblems.length > 0) {
      handleAddHtml();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [currentParsedProblems.length]); // currentParsedProblems의 개수가 변경될 때만

  // HTML 추가
  const handleAddHtml = () => {
    if (currentParsedProblems.length === 0) {
      return;
    }

    const beforeCount = accumulatedProblems.length;

    // 기존 문제와 중복 제거하며 병합
    const problemMap = new Map<number, string>();

    // 기존 누적 문제 추가
    accumulatedProblems.forEach((p) => {
      problemMap.set(p.problemId, p.solvedAt);
    });

    // 새로 추가될 문제 ID 추적
    const newProblemIds: number[] = [];

    // 새로 파싱한 문제 추가
    currentParsedProblems.forEach((p) => {
      if (!problemMap.has(p.problemId)) {
        newProblemIds.push(p.problemId);
      }
      problemMap.set(p.problemId, p.solvedAt);
    });

    const mergedProblems = Array.from(problemMap.entries()).map(([problemId, solvedAt]) => ({
      problemId,
      solvedAt,
    }));

    const afterCount = mergedProblems.length;
    const addedCount = afterCount - beforeCount; // 실제 추가된 개수
    const duplicateCount = currentParsedProblems.length - addedCount; // 중복 개수

    setAccumulatedProblems(mergedProblems);

    // 페이지 정보 추가
    setPageInfos((prev) => [
      ...prev,
      {
        pageNum: prev.length + 1,
        count: addedCount,
        duplicateCount: duplicateCount,
        problemIds: newProblemIds,
      },
    ]);

    setHtmlContent(''); // 입력 초기화

    if (duplicateCount > 0) {
      toast.success(`${addedCount}개 문제 추가 (중복 ${duplicateCount}개 제외, 총 ${mergedProblems.length}개)`);
    } else {
      toast.success(`${addedCount}개 문제 추가 (총 ${mergedProblems.length}개)`);
    }
  };

  // 페이지 삭제
  const handleRemovePage = (pageNum: number) => {
    const pageToRemove = pageInfos.find((p) => p.pageNum === pageNum);
    if (!pageToRemove) return;

    // 해당 페이지의 문제들 제거
    const remainingProblems = accumulatedProblems.filter((p) => !pageToRemove.problemIds.includes(p.problemId));
    setAccumulatedProblems(remainingProblems);

    // 페이지 정보에서 제거하고 페이지 번호 재정렬
    const updatedPages = pageInfos
      .filter((p) => p.pageNum !== pageNum)
      .map((p, index) => ({
        ...p,
        pageNum: index + 1,
      }));
    setPageInfos(updatedPages);
  };

  // 초기화
  const handleReset = () => {
    setAccumulatedProblems([]);
    setHtmlContent('');
    setPageInfos([]);
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
      <DialogContent className="bg-innerground-white flex max-h-[90vh] min-w-[80vw] flex-col">
        <DialogHeader>
          <div className="flex items-center justify-between">
            <div>
              <DialogTitle>가입 이전에 풀었던 문제 등록하기</DialogTitle>
              <DialogDescription>백준에서 HTML을 복사하여 과거 풀이 기록을 자동으로 등록할 수 있습니다.</DialogDescription>
            </div>
            <Popover>
              <PopoverTrigger asChild>
                <Button variant="ghost" size="icon" className="mr-10 h-8 w-8 shrink-0">
                  <HelpCircle className="text-muted-foreground h-5 w-5" />
                </Button>
              </PopoverTrigger>
              <PopoverContent className="w-80">
                <div className="space-y-2">
                  <h4 className="text-sm font-semibold">왜 이런 방식을 사용하나요?</h4>
                  <p className="text-muted-foreground text-xs">백준은 문제 풀이 시간 정보를 API로 제공하지 않습니다.</p>
                  <p className="text-muted-foreground text-xs">따라서 사용자가 직접 HTML을 제공하는 방식으로 안전하게 데이터를 가져옵니다.</p>
                  <p className="text-muted-foreground text-xs font-semibold">이 과정에서 서버는 어떤 크롤링도 하지 않으며, 오직 사용자가 제공한 HTML만을 브라우저에서 파싱합니다.</p>
                </div>
              </PopoverContent>
            </Popover>
          </div>
        </DialogHeader>

        <div className="flex-1 space-y-8 overflow-x-hidden overflow-y-auto pt-4 pr-4">
          {/* 1단계: 백준에서 HTML 복사 (좌우 분할) */}
          <div className="mb-20">
            <h3 className="mb-3 text-lg font-semibold">1단계: 백준에서 내가 푼 문제 복사</h3>
            <div className="mr-4 grid grid-cols-[35%_65%] gap-6">
              {/* 좌측: 버튼 및 설명 */}
              <div className="space-y-4">
                <Button variant="outline" onClick={() => window.open(baekjoonUrl, '_blank')} className="w-full" disabled={!bjAccountId}>
                  <ExternalLink className="mr-2 h-4 w-4" />
                  백준 채점현황 페이지 열기
                </Button>

                <div className="bg-innerground-hovergray/50 space-y-3 rounded-lg p-4">
                  <p className="text-sm font-semibold">1.5단계: HTML 복사 방법</p>
                  <ol className="list-inside list-decimal space-y-2 text-sm">
                    <li className="flex flex-wrap items-center gap-2">
                      <span>백준 페이지에서</span>
                      <kbd className="bg-muted border-border rounded border px-2 py-1 text-xs shadow-sm">Ctrl</kbd>
                      <span>+</span>
                      <kbd className="bg-muted border-border rounded border px-2 py-1 text-xs shadow-sm">Shift</kbd>
                      <span>+</span>
                      <kbd className="bg-muted border-border rounded border px-2 py-1 text-xs shadow-sm">C</kbd>
                      <span>누르기</span>
                    </li>
                    <li className="flex flex-wrap items-center gap-2">
                      <kbd className="bg-muted border-border rounded border px-2 py-1 text-xs shadow-sm">Ctrl</kbd>
                      <span>+</span>
                      <kbd className="bg-muted border-border rounded border px-2 py-1 text-xs shadow-sm">C</kbd>
                      <span>누르기</span>
                    </li>
                  </ol>
                  <p className="text-muted-foreground mt-2 text-xs">→ 개발자도구가 열리며 HTML이 자동 복사됩니다</p>
                  <p className="text-muted-foreground text-xs">※ F12 → Elements 탭 → {`<body>`}클릭 → Ctrl + C 누르기와 동일합니다</p>
                  <ol className="list-inside list-decimal space-y-2 text-sm">
                    <li className="mt-8 flex flex-wrap items-center gap-2">
                      <span>2단계로 가서</span>
                      <kbd className="bg-muted border-border rounded border px-2 py-1 text-xs shadow-sm">Ctrl</kbd>
                      <span>+</span>
                      <kbd className="bg-muted border-border rounded border px-2 py-1 text-xs shadow-sm">V</kbd>
                      <span>누르기</span>
                    </li>
                  </ol>
                </div>
              </div>

              {/* 우측: 이미지 캐러셀 (2장) */}
              <Carousel className="w-full">
                <CarouselContent>
                  <CarouselItem>
                    <div className="relative h-80 w-full">
                      <Image fill src="/guides/step1-no1.png" alt="이동 전 chuchutree 화면" className="rounded border object-contain shadow-sm" />
                    </div>
                  </CarouselItem>
                  <CarouselItem>
                    <div className="relative h-80 w-full">
                      <Image fill src="/guides/step1-no2.png" alt="이동 후 백준 화면" className="rounded border object-contain shadow-sm" />
                    </div>
                  </CarouselItem>
                </CarouselContent>
                <CarouselPrevious className="bg-primary text-innerground-white left-2" />
                <CarouselNext className="bg-primary text-innerground-white right-2" />
              </Carousel>
            </div>
          </div>

          {/* 2단계: 붙여넣기 및 등록 (좌우 분할) */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold">2단계: 붙여넣기 및 등록</h3>
              {accumulatedProblems.length > 0 && (
                <Button variant="outline" size="sm" onClick={handleReset}>
                  <RotateCcw className="mr-1 h-3 w-3" />
                  초기화
                </Button>
              )}
            </div>

            <div className="">
              {/* <div className="mr-4 grid grid-cols-[35%_65%] gap-6"> */}
              {/* 좌측: 붙여넣기 영역 */}
              <div className="space-y-4">
                <div
                  className="bg-innerground-hovergray/50 hover:bg-innerground-darkgray/70 border-input flex min-h-80 cursor-text flex-col justify-center rounded-md border-2 border-dashed p-6 transition-colors"
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

                  {/* 항상 표시되는 붙여넣기 안내 */}
                  <div className="mb-4 text-center">
                    <p className="text-muted-foreground flex flex-wrap items-center justify-center gap-2 text-sm">
                      <span>여기를 클릭하고</span>
                      <kbd className="bg-muted border-border rounded border px-2 py-1 text-xs shadow-sm">Ctrl</kbd>
                      <span>+</span>
                      <kbd className="bg-muted border-border rounded border px-2 py-1 text-xs shadow-sm">V</kbd>
                      <span>로 붙여넣기</span>
                    </p>
                  </div>

                  {/* 페이지 정보 목록 */}
                  {pageInfos.length > 0 && (
                    <div className="flex-1 space-y-4">
                      <div className="flex flex-wrap gap-3">
                        {pageInfos.map((page) => (
                          <div key={page.pageNum} className="bg-primary/10 border-primary relative flex items-center gap-2 rounded-lg border px-2 py-2">
                            <FileText className="text-primary h-5 w-5" />
                            <div className="text-sm">
                              <div className="flex items-center gap-2">
                                <span className="font-semibold">{page.pageNum}페이지</span>
                                <span className="text-foreground">{page.count}개</span>
                              </div>
                              {page.duplicateCount > 0 && <p className="text-muted-foreground text-xs">중복문제 {page.duplicateCount}개</p>}
                            </div>
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                handleRemovePage(page.pageNum);
                              }}
                              className="text-muted-foreground hover:text-destructive ml-2 transition-colors"
                            >
                              <X className="h-4 w-4" />
                            </button>
                          </div>
                        ))}
                      </div>

                      {/* 추가 안내 문구 */}
                      <div className="border-t pt-3">
                        <p className="text-muted-foreground text-center text-xs">
                          💡 여러 페이지를 추가하려면, 백준에서 <span className="text-primary">다음 페이지</span>로 이동하여
                          <br />
                          같은 방법으로 복사한 후 여기에 다시 붙여넣기 하세요
                        </p>
                        <p className="text-muted-foreground mt-2 text-center text-xs">
                          ※ F12 → Elements 탭 → <span className="text-primary">{`<body>`}클릭</span> → Ctrl + C
                        </p>
                      </div>
                    </div>
                  )}
                </div>
              </div>

              {/* 우측: 이미지 */}
              {/* <div className="relative h-80 w-full">
                <Image fill src="/guides/step2-no1.png" alt="붙여넣기 완료 화면" className="rounded border object-contain shadow-sm" />
              </div> */}
            </div>
          </div>

          {/* 안내 */}
          <div className="bg-innerground-hovergray/30 rounded-lg p-3">
            <p className="text-muted-foreground mb-1 text-xs">💡 이 기능은 백준 서버를 크롤링하지 않으며, 사용자가 직접 제공한 HTML만 브라우저에서 파싱합니다.</p>
            <p className="text-muted-foreground text-xs">💡 붙여넣기 하면 자동으로 문제가 추가되며, 중복된 문제는 자동으로 제거됩니다.</p>
          </div>

          {/* FAQ */}
          <Accordion type="single" collapsible>
            <AccordionItem value="faq">
              <AccordionTrigger className="text-sm font-semibold">문제가 발생했나요? (자주 묻는 질문)</AccordionTrigger>
              <AccordionContent className="space-y-4">
                <div className="space-y-2">
                  <p className="text-sm font-semibold">{`Q. "감지된 문제: 0개"로 표시됩니다`}</p>
                  <p className="text-muted-foreground text-xs">
                    A. body 태그 전체를 복사했는지 확인하세요. <kbd className="bg-muted rounded border px-1.5 py-0.5 text-xs">Ctrl</kbd>+
                    <kbd className="bg-muted rounded border px-1.5 py-0.5 text-xs">Shift</kbd>+<kbd className="bg-muted rounded border px-1.5 py-0.5 text-xs">C</kbd> 후 Elements 탭에서{' '}
                    <code className="bg-muted text-primary rounded px-1.5 py-0.5 text-xs">&lt;body&gt;</code> 태그가 하이라이트된 상태에서{' '}
                    <kbd className="bg-muted rounded border px-1.5 py-0.5 text-xs">Ctrl</kbd>+<kbd className="bg-muted rounded border px-1.5 py-0.5 text-xs">C</kbd>를 눌러야 합니다.
                  </p>
                  <p className="text-muted-foreground text-xs">
                    A. 혹은, 백준 화면에서 새로고침 이후 F12 → Elements 탭 → <span className="text-primary">{`<body>`}클릭</span> → Ctrl + C 누르기 → 2단계에 붙여넣기
                  </p>
                </div>

                <div className="space-y-2">
                  <p className="text-sm font-semibold">Q. 개발자도구가 열리지 않아요</p>
                  <p className="text-muted-foreground text-xs">
                    A. 브라우저마다 단축키가 다를 수 있습니다.
                    <br />• Chrome/Edge: <kbd className="bg-muted rounded border px-1.5 py-0.5 text-xs">Ctrl</kbd>+<kbd className="bg-muted rounded border px-1.5 py-0.5 text-xs">Shift</kbd>+
                    <kbd className="bg-muted rounded border px-1.5 py-0.5 text-xs">C</kbd>
                    <br />• Firefox: <kbd className="bg-muted rounded border px-1.5 py-0.5 text-xs">Ctrl</kbd>+<kbd className="bg-muted rounded border px-1.5 py-0.5 text-xs">Shift</kbd>+
                    <kbd className="bg-muted rounded border px-1.5 py-0.5 text-xs">I</kbd>
                    <br />• Safari (Mac): <kbd className="bg-muted rounded border px-1.5 py-0.5 text-xs">Cmd</kbd>+<kbd className="bg-muted rounded border px-1.5 py-0.5 text-xs">Option</kbd>+
                    <kbd className="bg-muted rounded border px-1.5 py-0.5 text-xs">C</kbd>
                  </p>
                </div>

                <div className="space-y-2">
                  <p className="text-sm font-semibold">Q. 여러 페이지를 추가할 수 있나요?</p>
                  <p className="text-muted-foreground text-xs">
                    A. 네, 가능합니다. 백준에서 다른 페이지로 이동하여 같은 과정을 반복한 후 붙여넣기 하면 자동으로 누적됩니다. 중복된 문제는 자동으로 제거됩니다.
                  </p>
                </div>

                <div className="space-y-2">
                  <p className="text-sm font-semibold">Q. 잘못 붙여넣었어요. 어떻게 하나요?</p>
                  <p className="text-muted-foreground text-xs">{`A. 우측 상단의 "초기화" 버튼을 클릭하면 모든 내용이 초기화됩니다. 걱정하지 마시고 다시 시도하세요.`}</p>
                </div>

                <div className="space-y-2">
                  <p className="text-sm font-semibold">Q. 이 기능은 안전한가요?</p>
                  <p className="text-muted-foreground text-xs">
                    A. 100% 안전합니다. 이 기능은 브라우저 내에서만 작동하며, 서버로 어떤 크롤링 요청도 보내지 않습니다. 오직 사용자가 직접 제공한 HTML만을 파싱합니다.
                  </p>
                </div>
              </AccordionContent>
            </AccordionItem>
          </Accordion>
          <div className="text-muted-foreground flex justify-end text-sm">등록 후 캘린더에서 풀었던 문제들을 확인하세요</div>
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
