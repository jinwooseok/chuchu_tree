'use client';

import { useState } from 'react';
import { RecommendedProblems, useRecommendationStore } from '@/lib/store/recommendation';
import { toast } from '@/lib/utils/toast';

// JSON 파일 import
import recommendation1 from '../mock/user-accounts_me_problems_1_260126.json';
import recommendation2 from '../mock/user-accounts_me_problems_2_260126.json';
import recommendation3 from '../mock/user-accounts_me_problems_3_260126.json';

// 3가지 추천 데이터
const RECOMMENDATION_DATA = [recommendation1, recommendation2, recommendation3];

/**
 * 랜딩페이지용 추천받기 훅
 * 3가지 JSON 데이터를 순환하며 표시
 */
export function useLandingRecommend() {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isPending, setIsPending] = useState(false);

  const {
    actions: { setProblems, setLoading, setError, addRecommendationHistory },
  } = useRecommendationStore();

  const recommend = () => {
    setIsPending(true);
    setLoading(true);
    setError(null);

    // 로딩 시뮬레이션 (500ms)
    setTimeout(() => {
      try {
        const currentData = RECOMMENDATION_DATA[currentIndex];
        const problems: RecommendedProblems[] = currentData.data.problems as RecommendedProblems[];

        // store에 데이터 설정
        setProblems(problems);
        setLoading(false);
        addRecommendationHistory(problems);

        // 다음 인덱스로 이동 (순환)
        setCurrentIndex((prev) => (prev + 1) % RECOMMENDATION_DATA.length);

        toast.success('문제 추천을 받았습니다.');
      } catch (error) {
        setError(error as Error);
        setLoading(false);
        toast.error('문제 추천에 실패했습니다.');
      } finally {
        setIsPending(false);
      }
    }, 500);
  };

  return { recommend, isPending };
}
