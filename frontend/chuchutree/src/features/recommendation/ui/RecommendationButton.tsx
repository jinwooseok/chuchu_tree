'use client';

import { Button } from '@/components/ui/button';
import { useRecommendationStore } from '@/lib/store/recommendation';
import { useCalendarStore } from '@/lib/store/calendar';
import { EyeOff, Search, SlidersHorizontal, ChevronDown, EllipsisVertical, History } from 'lucide-react';
import { useState } from 'react';
import { RecommendationHistoryDialog } from './RecommendationHistoryDialog';
import { useModal } from '@/lib/providers/modal-provider';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { TAG_INFO } from '@/shared/constants/tagSystem';
import { AppTooltip } from '@/components/custom/tooltip/AppTooltip';
import { useRecommend } from '../hooks/useRecommend';

export function RecommendationButton() {
  const { selectedDate } = useCalendarStore();
  const {
    selectedLevels,
    selectedTagsList,
    selectedExclusionMode,
    selectedCount,
    showFilters,
    showLevelSection,
    showTagSection,
    showFilterSection,
    showExcludedModeSection,
    actions: { setSelectedLevels, setSelectedTagsList, setSelectedExclusionMode, setSelectedCount, toggleFilter, resetFilters, toggleLevelSection, toggleTagSection, toggleFilterSection, toggleExcludedModeSection },
  } = useRecommendationStore();

  const [isCountPopoverOpen, setIsCountPopoverOpen] = useState(false);

  const { recommend, isPending } = useRecommend();
  const { openModal, closeModal } = useModal();

  const handleRecommend = () => {
    recommend();
  };

  // Level 토글 핸들러
  const toggleLevel = (level: string) => {
    setSelectedLevels(selectedLevels.includes(level) ? selectedLevels.filter((l) => l !== level) : [...selectedLevels, level]);
  };

  // Tag 토글 핸들러
  const toggleTag = (tag: string) => {
    setSelectedTagsList(selectedTagsList.includes(tag) ? selectedTagsList.filter((t) => t !== tag) : [...selectedTagsList, tag]);
  };
  // ExclusionMode 토글 핸들러
  const toggleExclusionMode = (mode: string) => {
    setSelectedExclusionMode(mode);
  };
  // count 토글 핸들러
  const toggleCount = (cnt: number) => {
    setSelectedCount(cnt);
    setIsCountPopoverOpen(false);
  };

  const levels = ['easy', 'normal', 'hard', 'extreme'] as const;
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
  const hasTagChanges = selectedTagsList.length > 0;
  const hasFilterChanges = JSON.stringify(showFilters) !== JSON.stringify(initialShowFilters);
  const hasLevelChanges = selectedLevels.length > 0;

  // Format selected date
  const formatSelectedDate = () => {
    if (!selectedDate) return '오늘!';
    const month = selectedDate.getMonth() + 1;
    const day = selectedDate.getDate();
    return `${month}월 ${day}일`;
  };

  const etcIsChanged = selectedExclusionMode !== 'LENIENT' || selectedCount !== 3;

  return (
    <div className="flex h-full gap-1">
      <div className="flex h-full w-50 flex-col gap-2 rounded-lg border-2 border-dashed p-2">
        {/* header */}
        <div className="flex items-center justify-between pl-2 text-xs">
          <div className="cursor-default text-center">{formatSelectedDate()}</div>
          {/* 버튼들 */}
          <div className="flex items-center justify-center">
            <div className="flex items-center justify-center gap-2">
              <AppTooltip content="알고리즘 유형 선택" side="top">
                <div aria-label="알고리즘 유형 선택창 열기" className="relative cursor-pointer" onClick={toggleTagSection}>
                  <Search className="text-muted-foreground h-4 w-4" />
                  {hasTagChanges && <div className="bg-primary/80 absolute top-0 -right-0.5 h-2 w-2 rounded-full" />}
                </div>
              </AppTooltip>
              <AppTooltip content="표시 항목" side="top">
                <div aria-label="표시 항목창 열기" className="relative cursor-pointer" onClick={toggleFilterSection}>
                  <EyeOff className="text-muted-foreground h-4 w-4" />
                  {hasFilterChanges && <div className="bg-primary/80 absolute top-0 -right-0.5 h-2 w-2 rounded-full" />}
                </div>
              </AppTooltip>
              <AppTooltip content="난이도 선택" side="top">
                <div aria-label="난이도 선택창 열기" className="relative cursor-pointer" onClick={toggleLevelSection}>
                  <SlidersHorizontal className="text-muted-foreground h-4 w-4" />
                  {hasLevelChanges && <div className="bg-primary/80 absolute top-0 -right-0.5 h-2 w-2 rounded-full" />}
                </div>
              </AppTooltip>
            </div>
            <div className="ml-1">
              <AppTooltip content="기타 설정" side="top">
                <div aria-label="기타 설정창 열기" className="relative cursor-pointer" onClick={toggleExcludedModeSection}>
                  <EllipsisVertical className="text-muted-foreground h-4 w-4" />
                  {selectedExclusionMode !== 'LENIENT' && <div className="bg-primary/80 absolute top-0 -right-0.5 h-2 w-2 rounded-full" />}
                </div>
              </AppTooltip>
            </div>
          </div>
        </div>
        {/* 추천받기 */}
        <Button aria-label="알고리즘 문제 추천받기" className="selcect-none flex-1 cursor-pointer" onClick={handleRecommend} disabled={isPending}>
          {isPending ? '추천 중...' : '추천 받기'}
        </Button>
        {/* 추천 기록 버튼 */}
        <Button
          aria-label="추천 기록 보기"
          variant="outline"
          size="sm"
          className="text-muted-foreground hover:text-muted-foreground h-7 cursor-pointer text-xs"
          onClick={() => {
            openModal('recommendation-history', <RecommendationHistoryDialog onClose={() => closeModal('recommendation-history')} />);
          }}
        >
          <History className="mr-1 h-3 w-3" />
          추천 기록
        </Button>
        {/* 알고리즘 유형 멀티셀렉트 */}
        {showTagSection && (
          <Popover>
            <AppTooltip content="선택한 알고리즘 유형만 추천됩니다." side="right">
              <PopoverTrigger asChild>
                <Button aria-label="알고리즘 유형 선택" variant="outline" className="w-full cursor-pointer justify-between text-xs">
                  {selectedTagsList.length > 0 ? `${selectedTagsList.length}개 선택됨` : '알고리즘 선택'}
                  <ChevronDown className="ml-2 h-4 w-4" />
                </Button>
              </PopoverTrigger>
            </AppTooltip>
            <PopoverContent className="w-64 p-2">
              <div className="max-h-64 space-y-2 overflow-y-auto">
                {Object.entries(TAG_INFO).map(([tagKey, tagInfo]) => (
                  <label key={tagKey} aria-label={tagInfo.kr} className="hover:bg-background/60 flex cursor-pointer items-center gap-2 rounded p-1">
                    <input
                      type="checkbox"
                      checked={selectedTagsList.includes(tagKey)}
                      onChange={() => toggleTag(tagKey)}
                      className="checked:bg-primary checked:border-primary border-muted-foreground h-4 w-4 cursor-pointer appearance-none rounded border-2"
                    />
                    <span className="text-xs">{tagInfo.kr}</span>
                  </label>
                ))}
              </div>
              {selectedTagsList.length > 0 && (
                <div className="mt-2 flex justify-end border-t pt-2">
                  <button onClick={() => setSelectedTagsList([])} className="text-muted-foreground hover:text-foreground text-xs underline">
                    전체 해제
                  </button>
                </div>
              )}
            </PopoverContent>
          </Popover>
        )}
      </div>
      <div className={`h-full rounded-lg ${showLevelSection || showFilterSection ? 'w-26 border-2 border-dashed p-2' : showExcludedModeSection ? 'w-40 border-2 border-dashed p-2' : ''}`}>
        {showLevelSection && (
          <div>
            <div className="text-muted-foreground mb-4 cursor-default text-xs font-semibold">난이도 선택</div>
            <div className="space-y-5">
              {levels.map((level) => (
                <label key={level} aria-label={level} className="hover:bg-background/60 flex cursor-pointer items-center gap-2 rounded">
                  <input
                    type="checkbox"
                    checked={selectedLevels.includes(level)}
                    onChange={() => toggleLevel(level)}
                    className="checked:bg-primary checked:border-primary border-muted-foreground h-4 w-4 cursor-pointer appearance-none rounded border-2"
                  />
                  <span className="text-xs capitalize">{level}</span>
                </label>
              ))}
            </div>
            {selectedLevels.length > 0 && (
              <div className="mt-4 mr-2 flex justify-end">
                <button onClick={() => setSelectedLevels([])} aria-label="난이도 선택 초기화" className="text-muted-foreground hover:text-muted-foreground text-xs underline">
                  전체 해제
                </button>
              </div>
            )}
          </div>
        )}

        {showFilterSection && (
          <div>
            <div className="text-muted-foreground mb-4 cursor-default text-xs font-semibold">표시 항목</div>
            <div className="space-y-5">
              {filters.map((filter) => (
                <label key={filter.key} aria-label={filter.label} className="hover:bg-background/60 flex cursor-pointer items-center gap-2 rounded">
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
              <div className="mt-4 mr-2 flex justify-end">
                <button onClick={resetFilters} aria-label="표시 항목 초기화" className="text-muted-foreground hover:text-foreground text-xs underline">
                  초기화
                </button>
              </div>
            )}
          </div>
        )}
        {showExcludedModeSection && (
          <div>
            <div className="text-muted-foreground mb-2 cursor-default text-xs font-semibold">제외된 태그 설정</div>
            <div className="space-y-2">
              <label key="ExcludedModeSTRICT" aria-label="ExcludedModeSTRICT" className="hover:bg-background/60 flex cursor-pointer items-start gap-2 rounded">
                <input
                  type="checkbox"
                  checked={selectedExclusionMode === 'STRICT'}
                  onChange={() => toggleExclusionMode('STRICT')}
                  className="checked:bg-primary checked:border-primary border-muted-foreground h-4 w-4 shrink-0 cursor-pointer appearance-none rounded border-2"
                />
                <div className="flex flex-col gap-1">
                  <span className="text-xs">엄격한 제외</span>
                  <span className="text-muted-foreground text-xs">제외된 유형이 절대 추천되지 않음</span>
                </div>
              </label>
              <label key="ExcludedModeLENIENT" aria-label="ExcludedModeLENIENT" className="hover:bg-background/60 flex cursor-pointer items-start gap-2 rounded">
                <input
                  type="checkbox"
                  checked={selectedExclusionMode === 'LENIENT'}
                  onChange={() => toggleExclusionMode('LENIENT')}
                  className="checked:bg-primary checked:border-primary border-muted-foreground h-4 w-4 shrink-0 cursor-pointer appearance-none rounded border-2"
                />
                <div className="flex flex-col gap-1">
                  <span className="text-xs">느슨한 제외</span>
                  <span className="text-muted-foreground text-xs">제외된 유형 때문에 추천되지는 않음</span>
                </div>
              </label>
            </div>
            <div className="mt-2 mr-2 flex items-center justify-between text-xs">
              <div className="text-muted-foreground cursor-default font-semibold">추천 문제수</div>
              <Popover open={isCountPopoverOpen} onOpenChange={setIsCountPopoverOpen}>
                <PopoverTrigger asChild>
                  <Button aria-label="문제수 선택" variant="outline" className="h-6 w-4 cursor-pointer text-xs">
                    {selectedCount}
                  </Button>
                </PopoverTrigger>
                <PopoverContent className="w-16 p-2">
                  <div className="max-h-64 space-y-2 overflow-y-auto">
                    {[1, 2, 3, 4, 5, 6].map((cnt) => (
                      <label key={`문제수${cnt}`} aria-label={`문제수${cnt}`} className="hover:bg-background/60 flex cursor-pointer items-center gap-2 rounded p-1">
                        <input
                          type="checkbox"
                          checked={selectedCount === cnt}
                          onChange={() => toggleCount(cnt)}
                          className="checked:bg-primary checked:border-primary border-muted-foreground h-4 w-4 cursor-pointer appearance-none rounded border-2"
                        />
                        <span className="text-xs">{cnt}</span>
                      </label>
                    ))}
                  </div>
                </PopoverContent>
              </Popover>
            </div>
            {etcIsChanged && (
              <div className="mt-2 mr-2 flex justify-end">
                <button
                  onClick={() => {
                    toggleExclusionMode('LENIENT');
                    setSelectedCount(3);
                  }}
                  aria-label="제외된 태그 설정 초기화"
                  className="text-muted-foreground hover:text-foreground text-xs underline"
                >
                  초기화
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
