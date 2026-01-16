'use client';

import { Button } from '@/components/ui/button';
import { useRecommendationStore } from '@/lib/store/recommendation';
import { useGetRecommendation } from '@/entities/recommendation';
import { useCalendarStore } from '@/lib/store/calendar';
import { toast } from 'sonner';
import { EyeOff, Search, SlidersHorizontal, ChevronDown } from 'lucide-react';
import { useState } from 'react';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { TAG_INFO } from '@/shared/constants/tagSystem';
import { AppTooltip } from '@/components/custom/tooltip/AppTooltip';

export function RecommendationButton() {
  const { selectedDate } = useCalendarStore();
  const {
    showFilters,
    showLevelSection,
    showTagSection,
    showFilterSection,
    actions: { setProblems, setLoading, setError, toggleFilter, resetFilters, toggleLevelSection, toggleTagSection, toggleFilterSection },
  } = useRecommendationStore();

  // 로컬 state로 복수 선택 관리
  const [selectedLevels, setSelectedLevels] = useState<string[]>([]);
  const [selectedTagsList, setSelectedTagsList] = useState<string[]>([]);

  const { mutate: getRecommendation, isPending } = useGetRecommendation();

  const handleGetRecommendation = (params: { level: string; tags: string }) => {
    getRecommendation(params, {
      onSuccess: (data) => {
        setProblems(data.problems);
        setLoading(false);
        toast.success('문제 추천을 받았습니다.', {
          position: 'top-center',
        });
      },
      onError: (error) => {
        setError(error);
        setLoading(false);
        toast.error('문제 추천에 실패했습니다.', {
          position: 'top-center',
        });
      },
    });
  };

  const handleRecommend = () => {
    setLoading(true);
    setError(null);

    // 배열을 JSON 문자열로 변환 (level은 대문자로)
    const levelParam = selectedLevels.length === 0 ? '[]' : JSON.stringify(selectedLevels.map((l) => l.toUpperCase()));

    const tagsParam = selectedTagsList.length === 0 ? '[]' : JSON.stringify(selectedTagsList);

    handleGetRecommendation({
      level: levelParam,
      tags: tagsParam,
    });
  };

  // Level 토글 핸들러
  const toggleLevel = (level: string) => {
    setSelectedLevels((prev) => (prev.includes(level) ? prev.filter((l) => l !== level) : [...prev, level]));
  };

  // Tag 토글 핸들러
  const toggleTag = (tag: string) => {
    setSelectedTagsList((prev) => (prev.includes(tag) ? prev.filter((t) => t !== tag) : [...prev, tag]));
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

  return (
    <div className="flex h-full gap-1">
      <div className="flex h-full w-50 flex-col gap-2 rounded-lg border-2 border-dashed p-2">
        {/* header */}
        <div className="flex items-center justify-between px-2 text-xs">
          <div className="cursor-default text-center">{formatSelectedDate()}</div>
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
        </div>
        {/* 추천받기 */}
        <Button aria-label="알고리즘 문제 추천받기" className="selcect-none flex-1 cursor-pointer" onClick={handleRecommend} disabled={isPending}>
          {isPending ? '추천 중...' : '추천 받기'}
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
      <div className={`h-full rounded-lg ${showLevelSection || showFilterSection ? 'w-26 border-2 border-dashed p-2' : ''}`}>
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
      </div>
    </div>
  );
}
