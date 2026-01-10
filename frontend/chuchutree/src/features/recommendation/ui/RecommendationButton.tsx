'use client';

import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useRecommendationStore } from '@/lib/store/recommendation';
import { useGetRecommendation } from '@/entities/recommendation';
import { useCalendarStore } from '@/lib/store/calendar';
import { toast } from 'sonner';
import { EyeOff, Search, SlidersHorizontal } from 'lucide-react';

export function RecommendationButton() {
  const { selectedDate } = useCalendarStore();
  const {
    selectedLevel,
    selectedTags,
    showFilters,
    showLevelSection,
    showTagSection,
    showFilterSection,
    actions: { setSelectedLevel, setSelectedTags, setProblems, setLoading, setError, toggleFilter, resetFilters, toggleLevelSection, toggleTagSection, toggleFilterSection },
  } = useRecommendationStore();

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
    handleGetRecommendation({
      level: selectedLevel || '',
      tags: selectedTags || '',
    });
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
  const hasTagChanges = selectedTags !== '';
  const hasFilterChanges = JSON.stringify(showFilters) !== JSON.stringify(initialShowFilters);
  const hasLevelChanges = selectedLevel !== null;

  // Format selected date
  const formatSelectedDate = () => {
    if (!selectedDate) return '날짜 선택 필요';
    const month = selectedDate.getMonth() + 1;
    const day = selectedDate.getDate();
    return `${month}월 ${day}일`;
  };

  return (
    <div className="flex h-full gap-1">
      <div className="flex h-full w-50 flex-col gap-2 rounded-lg border-2 border-dashed p-2">
        {/* header */}
        <div className="flex items-center justify-between px-2 text-xs">
          <div className="text-center">{formatSelectedDate()}</div>
          <div className="flex items-center justify-center gap-2">
            <div title="알고리즘 유형 검색" className="relative" onClick={toggleTagSection}>
              <Search className="text-muted-foreground h-4 w-4 cursor-pointer" />
              {hasTagChanges && <div className="bg-primary/80 absolute top-0 -right-0.5 h-2 w-2 rounded-full" />}
            </div>
            <div title="표시 항목" className="relative" onClick={toggleFilterSection}>
              <EyeOff className="text-muted-foreground h-4 w-4 cursor-pointer" />
              {hasFilterChanges && <div className="bg-primary/80 absolute top-0 -right-0.5 h-2 w-2 rounded-full" />}
            </div>
            <div title="난이도 선택" className="relative" onClick={toggleLevelSection}>
              <SlidersHorizontal className="text-muted-foreground h-4 w-4 cursor-pointer" />
              {hasLevelChanges && <div className="bg-primary/80 absolute top-0 -right-0.5 h-2 w-2 rounded-full" />}
            </div>
          </div>
        </div>
        {/* 추천받기 */}
        <Button className="flex-1" onClick={handleRecommend} disabled={isPending}>
          {isPending ? '추천 중...' : '추천 받기'}
        </Button>
        {/* 알고리즘 유형 검색창 */}
        {showTagSection && (
          <div className="relative">
            <Search className="text-muted-foreground absolute top-1/2 left-2 h-4 w-4 -translate-y-1/2" />
            <Input className="pl-8" placeholder="선택된 유형만 추천받습니다." value={selectedTags} onChange={(e) => setSelectedTags(e.target.value)} />
          </div>
        )}
      </div>
      <div className={`h-full rounded-lg ${showLevelSection || showFilterSection ? 'w-26 border-2 border-dashed p-2' : ''}`}>
        {showLevelSection && (
          <div>
            <div className="text-muted-foreground mb-4 text-xs font-semibold">난이도 선택</div>
            <div className="space-y-5">
              {levels.map((level) => (
                <label key={level} className="hover:bg-background/60 flex cursor-pointer items-center gap-2 rounded">
                  <input
                    type="radio"
                    name="level"
                    checked={selectedLevel === level}
                    onChange={() => setSelectedLevel(level)}
                    className="checked:bg-primary checked:border-primary border-muted-foreground h-4 w-4 cursor-pointer appearance-none rounded-full border-2"
                  />
                  <span className="text-xs capitalize">{level}</span>
                </label>
              ))}
            </div>
            {selectedLevel && (
              <div className="mt-4 mr-2 flex justify-end">
                <button onClick={() => setSelectedLevel(null)} className="text-muted-foreground hover:text-muted-foreground text-xs underline">
                  선택 해제
                </button>
              </div>
            )}
          </div>
        )}

        {showFilterSection && (
          <div>
            <div className="text-muted-foreground mb-4 text-xs font-semibold">표시 항목</div>
            <div className="space-y-5">
              {filters.map((filter) => (
                <label key={filter.key} className="hover:bg-background/60 flex cursor-pointer items-center gap-2 rounded">
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
                <button onClick={resetFilters} className="text-muted-foreground hover:text-foreground text-xs underline">
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
