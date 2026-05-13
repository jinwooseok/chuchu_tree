import { useRecommendationStore, RecommendedProblems } from '../recommendation';

describe('RecommendationStore', () => {
  beforeEach(() => {
    // 각 테스트 전 store reset
    const { reset } = useRecommendationStore.getState();
    reset();
  });

  it('초기 상태가 올바르게 설정된다', () => {
    const store = useRecommendationStore.getState();

    expect(store.selectedLevels).toEqual([]);
    expect(store.selectedTagsList).toEqual([]);
    expect(store.selectedExclusionMode).toBe('LENIENT');
    expect(store.selectedCount).toBe(3);
    expect(store.problems).toEqual([]);
    expect(store.isLoading).toBe(false);
    expect(store.error).toBeNull();
    expect(store.recommendationHistory).toEqual([]);
    expect(store.showFilters).toEqual({
      problemNumber: true,
      problemTier: true,
      recommendReason: true,
      algorithm: false,
    });
    expect(store.showLevelSection).toBe(false);
    expect(store.showTagSection).toBe(false);
    expect(store.showFilterSection).toBe(false);
    expect(store.showExcludedModeSection).toBe(false);
  });

  it('난이도를 설정한다 (복수 선택 + 빈 배열)', () => {
    const store = useRecommendationStore.getState();

    store.setSelectedLevels(['easy', 'normal']);
    expect(useRecommendationStore.getState().selectedLevels).toEqual(['easy', 'normal']);

    store.setSelectedLevels([]);
    expect(useRecommendationStore.getState().selectedLevels).toEqual([]);
  });

  it('태그를 설정한다 (복수 선택 + 빈 배열)', () => {
    const store = useRecommendationStore.getState();

    store.setSelectedTagsList(['dp', 'greedy']);
    expect(useRecommendationStore.getState().selectedTagsList).toEqual(['dp', 'greedy']);

    store.setSelectedTagsList([]);
    expect(useRecommendationStore.getState().selectedTagsList).toEqual([]);
  });

  it('추천 결과를 클리어한다', () => {
    const store = useRecommendationStore.getState();

    // 임의의 문제 데이터 설정
    const mockProblems: RecommendedProblems[] = [
      {
        problemId: 1000,
        problemTitle: '테스트 문제',
        problemTierLevel: 10,
        problemTierName: 'Gold V',
        problemClassLevel: 3,
        recommandReasons: [],
        tags: [],
      },
    ];

    store.setProblems(mockProblems);
    store.setLoading(true);
    store.setError(new Error('테스트 에러'));

    expect(useRecommendationStore.getState().problems).toEqual(mockProblems);
    expect(useRecommendationStore.getState().isLoading).toBe(true);
    expect(useRecommendationStore.getState().error).not.toBeNull();

    // 클리어
    store.clearRecommendation();

    const clearedStore = useRecommendationStore.getState();
    expect(clearedStore.problems).toEqual([]);
    expect(clearedStore.isLoading).toBe(false);
    expect(clearedStore.error).toBeNull();
  });

  it('표시 필터를 토글한다', () => {
    const store = useRecommendationStore.getState();

    // problemNumber 토글
    expect(store.showFilters.problemNumber).toBe(true);
    store.toggleFilter('problemNumber');
    expect(useRecommendationStore.getState().showFilters.problemNumber).toBe(false);
    store.toggleFilter('problemNumber');
    expect(useRecommendationStore.getState().showFilters.problemNumber).toBe(true);

    // algorithm 토글
    expect(useRecommendationStore.getState().showFilters.algorithm).toBe(false);
    store.toggleFilter('algorithm');
    expect(useRecommendationStore.getState().showFilters.algorithm).toBe(true);
  });

  it('필터를 초기화한다', () => {
    const store = useRecommendationStore.getState();

    // 필터 변경
    store.toggleFilter('problemNumber');
    store.toggleFilter('algorithm');

    expect(useRecommendationStore.getState().showFilters.problemNumber).toBe(false);
    expect(useRecommendationStore.getState().showFilters.algorithm).toBe(true);

    // 필터 초기화
    store.resetFilters();

    const resetStore = useRecommendationStore.getState();
    expect(resetStore.showFilters).toEqual({
      problemNumber: true,
      problemTier: true,
      recommendReason: true,
      algorithm: false,
    });
  });

  it('Level Section을 열면 다른 section들이 닫힌다', () => {
    const store = useRecommendationStore.getState();

    // 다른 section들 열기
    store.toggleFilterSection();
    expect(useRecommendationStore.getState().showFilterSection).toBe(true);
    store.toggleExcludedModeSection();
    expect(useRecommendationStore.getState().showExcludedModeSection).toBe(true);

    // Level Section 열기
    store.toggleLevelSection();

    const updatedStore = useRecommendationStore.getState();
    expect(updatedStore.showLevelSection).toBe(true);
    expect(updatedStore.showFilterSection).toBe(false);
    expect(updatedStore.showExcludedModeSection).toBe(false);
  });

  it('Filter Section을 열면 다른 section들이 닫힌다', () => {
    const store = useRecommendationStore.getState();

    // 다른 section들 열기
    store.toggleLevelSection();
    expect(useRecommendationStore.getState().showLevelSection).toBe(true);
    store.toggleExcludedModeSection();

    expect(useRecommendationStore.getState().showExcludedModeSection).toBe(true);

    // Filter Section 열기
    store.toggleFilterSection();

    const updatedStore = useRecommendationStore.getState();
    expect(updatedStore.showFilterSection).toBe(true);
    expect(updatedStore.showLevelSection).toBe(false);
    expect(updatedStore.showExcludedModeSection).toBe(false);
  });

  it('ExcludedMode Section을 열면 다른 section들이 닫힌다', () => {
    const store = useRecommendationStore.getState();

    // 다른 section들 열기
    store.toggleLevelSection();
    expect(useRecommendationStore.getState().showLevelSection).toBe(true);
    store.toggleFilterSection();

    expect(useRecommendationStore.getState().showFilterSection).toBe(true);

    // ExcludedMode Section 열기
    store.toggleExcludedModeSection();

    const updatedStore = useRecommendationStore.getState();
    expect(updatedStore.showExcludedModeSection).toBe(true);
    expect(updatedStore.showLevelSection).toBe(false);
    expect(updatedStore.showFilterSection).toBe(false);
  });

  it('추천 히스토리를 추가한다', () => {
    const store = useRecommendationStore.getState();

    const mockProblem: RecommendedProblems = {
      problemId: 1000,
      problemTitle: '테스트 문제',
      problemTierLevel: 10,
      problemTierName: 'Gold V',
      problemClassLevel: 3,
      recommandReasons: [],
      tags: [],
    };

    store.addRecommendationHistory([mockProblem]);

    const updatedStore = useRecommendationStore.getState();
    expect(updatedStore.recommendationHistory).toHaveLength(1);
    expect(updatedStore.recommendationHistory[0].problems).toEqual([mockProblem]);
    expect(updatedStore.recommendationHistory[0].timestamp).toBeGreaterThan(0);
  });

  it('추천 히스토리가 최대 50개로 제한된다', () => {
    const store = useRecommendationStore.getState();

    const mockProblem: RecommendedProblems = {
      problemId: 1000,
      problemTitle: '테스트 문제',
      problemTierLevel: 10,
      problemTierName: 'Gold V',
      problemClassLevel: 3,
      recommandReasons: [],
      tags: [],
    };

    // 51개 추가
    for (let i = 0; i < 51; i++) {
      store.addRecommendationHistory([{ ...mockProblem, problemId: 1000 + i }]);
    }

    const updatedStore = useRecommendationStore.getState();
    expect(updatedStore.recommendationHistory).toHaveLength(50);
    // 가장 최근 항목이 가장 앞에 있어야 함 (unshift 사용)
    expect(updatedStore.recommendationHistory[0].problems[0].problemId).toBe(1050);
    // 가장 오래된 항목이 제거되었는지 검증
    expect(updatedStore.recommendationHistory[49].problems[0].problemId).toBe(1001);
  });

  it('추천 히스토리를 클리어한다', () => {
    const store = useRecommendationStore.getState();

    const mockProblem: RecommendedProblems = {
      problemId: 1000,
      problemTitle: '테스트 문제',
      problemTierLevel: 10,
      problemTierName: 'Gold V',
      problemClassLevel: 3,
      recommandReasons: [],
      tags: [],
    };

    store.addRecommendationHistory([mockProblem]);
    expect(useRecommendationStore.getState().recommendationHistory).toHaveLength(1);

    store.clearRecommendationHistory();
    expect(useRecommendationStore.getState().recommendationHistory).toEqual([]);
  });

  it('전체 상태를 초기화한다', () => {
    const store = useRecommendationStore.getState();

    // 여러 상태 변경
    store.setSelectedLevels(['easy', 'normal']);
    store.setSelectedTagsList(['dp', 'greedy']);
    store.setSelectedCount(5);
    store.toggleFilter('problemNumber');
    store.toggleLevelSection();

    const beforeReset = useRecommendationStore.getState();
    expect(beforeReset.selectedLevels).toEqual(['easy', 'normal']);
    expect(beforeReset.selectedCount).toBe(5);
    expect(beforeReset.showLevelSection).toBe(true);

    // 전체 초기화
    store.reset();

    const afterReset = useRecommendationStore.getState();
    expect(afterReset.selectedLevels).toEqual([]);
    expect(afterReset.selectedTagsList).toEqual([]);
    expect(afterReset.selectedCount).toBe(3);
    expect(afterReset.showFilters.problemNumber).toBe(true);
    expect(afterReset.showLevelSection).toBe(false);
  });
});
