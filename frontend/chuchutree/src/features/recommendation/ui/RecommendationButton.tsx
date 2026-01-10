'use client';

import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useRecommendationStore } from '@/lib/store/recommendation';
import { useGetRecommendation } from '@/entities/recommendation';
import { toast } from 'sonner';

export function RecommendationButton() {
  const {
    selectedLevel,
    selectedTags,
    showFilters,
    actions: { setSelectedLevel, setSelectedTags, setProblems, setLoading, setError, toggleFilter },
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

  return (
    <div className="flex h-full flex-col gap-2 rounded-lg border-2 border-dashed p-2">
      <Button className="flex-1" onClick={handleRecommend} disabled={isPending}>
        {isPending ? '추천 중...' : '추천 받기'}
      </Button>

      <div className="flex justify-between gap-2">
        {levels.map((level) => (
          <Button
            key={level}
            className="h-6 px-2 py-0 text-[10px]"
            variant={selectedLevel === level ? 'default' : 'outline'}
            onClick={() => setSelectedLevel(selectedLevel === level ? null : level)}
          >
            {level}
          </Button>
        ))}
      </div>

      <div className="flex items-center gap-2 rounded-lg border px-2">
        <p className="text-xs">TAG</p>
        <Input
          className="border-none"
          placeholder="All"
          value={selectedTags}
          onChange={(e) => setSelectedTags(e.target.value)}
        />
      </div>

      <div className="flex justify-between gap-1">
        {filters.map((filter) => (
          <Button
            key={filter.key}
            className="h-6 px-2 py-0 text-[10px]"
            variant={showFilters[filter.key] ? 'default' : 'outline'}
            onClick={() => toggleFilter(filter.key)}
          >
            {filter.label}
          </Button>
        ))}
      </div>
    </div>
  );
}
