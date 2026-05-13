'use client';

import { useGetStudyRecommendation } from '@/entities/study';
import { useStudyRecommendStore } from '@/lib/store/studyRecommend';
import { toast } from '@/lib/utils/toast';

export function useStudyRecommend(studyId: number) {
  const { mutate: getRecommendation, isPending } = useGetStudyRecommendation();
  const {
    targetMemberId,
    recommendAllUnsolved,
    selectedLevels,
    selectedTagsList,
    selectedExclusionMode,
    selectedCount,
    setProblems,
    setLoading,
  } = useStudyRecommendStore();

  const recommend = () => {
    setLoading(true);

    const levelParam = selectedLevels.length === 0 ? '[]' : JSON.stringify(selectedLevels.map((l) => l.toUpperCase()));
    const tagsParam = selectedTagsList.length === 0 ? '[]' : JSON.stringify(selectedTagsList);

    getRecommendation(
      {
        study_id: studyId,
        target_user_account_id: targetMemberId || null,
        recommend_all_unsolved: recommendAllUnsolved,
        count: selectedCount,
        level: levelParam,
        tags: tagsParam,
        exclusion_mode: selectedExclusionMode,
      },
      {
        onSuccess: (data) => {
          setProblems(data.problems);
          setLoading(false);
          toast.success('문제 추천을 받았습니다.');
        },
        onError: () => {
          setLoading(false);
          toast.error('문제 추천에 실패했습니다.');
        },
      },
    );
  };

  return { recommend, isPending };
}
