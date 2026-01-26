'use client';

import { useGetRecommendation } from '@/entities/recommendation';
import { useRecommendationStore } from '@/lib/store/recommendation';
import { toast } from '@/lib/utils/toast';

/**
 * 추천받기 로직을 재사용 가능한 훅으로 분리
 * store에서 필터 상태를 읽어와서 추천 API 호출
 */
export function useRecommend() {
  const { mutate: getRecommendation, isPending } = useGetRecommendation();
  const {
    selectedLevels,
    selectedTagsList,
    selectedExclusionMode,
    selectedCount,
    actions: { setProblems, setLoading, setError, addRecommendationHistory },
  } = useRecommendationStore();

  const recommend = () => {
    setLoading(true);
    setError(null);

    // 배열을 JSON 문자열로 변환 (level은 대문자로)
    const levelParam = selectedLevels.length === 0 ? '[]' : JSON.stringify(selectedLevels.map((l) => l.toUpperCase()));
    const tagsParam = selectedTagsList.length === 0 ? '[]' : JSON.stringify(selectedTagsList);

    getRecommendation(
      {
        level: levelParam,
        tags: tagsParam,
        count: selectedCount,
        exclusion_mode: selectedExclusionMode,
      },
      {
        onSuccess: (data) => {
          setProblems(data.problems);
          setLoading(false);
          addRecommendationHistory(data.problems);
          toast.success('문제 추천을 받았습니다.');
        },
        onError: (error) => {
          setError(error);
          setLoading(false);
          toast.error('문제 추천에 실패했습니다.');
        },
      },
    );
  };

  return { recommend, isPending };
}
