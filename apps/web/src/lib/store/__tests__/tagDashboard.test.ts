import { useTagDashboardSidebarStore } from '../tagDashboard';

describe('TagDashboardStore', () => {
  beforeEach(() => {
    // 각 테스트 전 store 초기화
    useTagDashboardSidebarStore.setState({
      searchQuery: '',
      sortBy: 'progress',
      sortDirection: 'asc',
      selectedTagId: null,
      categoryVisibility: {
        INTERMEDIATE: true,
        ADVANCED: true,
        MASTER: false,
        LOCKED: true,
        EXCLUDED: false,
      },
      categoryOrder: ['INTERMEDIATE', 'ADVANCED', 'MASTER', 'LOCKED', 'EXCLUDED'],
    });
  });

  it('초기 상태가 올바르게 설정된다', () => {
    const state = useTagDashboardSidebarStore.getState();

    expect(state.searchQuery).toBe('');
    expect(state.sortBy).toBe('progress');
    expect(state.sortDirection).toBe('asc');
    expect(state.selectedTagId).toBeNull();
    expect(state.categoryVisibility).toEqual({
      INTERMEDIATE: true,
      ADVANCED: true,
      MASTER: false,
      LOCKED: true,
      EXCLUDED: false,
    });
  });

  it('검색어를 설정한다', () => {
    const { setSearchQuery } = useTagDashboardSidebarStore.getState();

    setSearchQuery('그리디');
    expect(useTagDashboardSidebarStore.getState().searchQuery).toBe('그리디');

    setSearchQuery('');
    expect(useTagDashboardSidebarStore.getState().searchQuery).toBe('');
  });

  it('정렬 기준을 변경한다', () => {
    const { setSortBy } = useTagDashboardSidebarStore.getState();

    setSortBy('name');
    expect(useTagDashboardSidebarStore.getState().sortBy).toBe('name');

    setSortBy('lastSolved');
    expect(useTagDashboardSidebarStore.getState().sortBy).toBe('lastSolved');

    setSortBy('level');
    expect(useTagDashboardSidebarStore.getState().sortBy).toBe('level');
  });

  it('sortBy를 progress로 변경하면 MASTER와 EXCLUDED가 자동으로 false가 된다', () => {
    const { toggleCategoryVisibility, setSortBy } = useTagDashboardSidebarStore.getState();

    // MASTER와 EXCLUDED를 true로 설정
    toggleCategoryVisibility('MASTER');
    toggleCategoryVisibility('EXCLUDED');

    const beforeState = useTagDashboardSidebarStore.getState();
    expect(beforeState.categoryVisibility.MASTER).toBe(true);
    expect(beforeState.categoryVisibility.EXCLUDED).toBe(true);

    // sortBy를 progress로 변경
    setSortBy('progress');

    const afterState = useTagDashboardSidebarStore.getState();
    expect(afterState.sortBy).toBe('progress');
    expect(afterState.categoryVisibility.MASTER).toBe(false);
    expect(afterState.categoryVisibility.EXCLUDED).toBe(false);
  });

  it('태그를 선택하고 해제한다', () => {
    const { setSelectedTagId } = useTagDashboardSidebarStore.getState();

    setSelectedTagId(123);
    expect(useTagDashboardSidebarStore.getState().selectedTagId).toBe(123);

    setSelectedTagId(null);
    expect(useTagDashboardSidebarStore.getState().selectedTagId).toBeNull();

    setSelectedTagId(456);
    expect(useTagDashboardSidebarStore.getState().selectedTagId).toBe(456);
  });

  it('카테고리 표시/숨김을 토글한다', () => {
    const { toggleCategoryVisibility } = useTagDashboardSidebarStore.getState();

    const initialState = useTagDashboardSidebarStore.getState();
    expect(initialState.categoryVisibility.INTERMEDIATE).toBe(true);

    toggleCategoryVisibility('INTERMEDIATE');
    expect(useTagDashboardSidebarStore.getState().categoryVisibility.INTERMEDIATE).toBe(false);

    toggleCategoryVisibility('INTERMEDIATE');
    expect(useTagDashboardSidebarStore.getState().categoryVisibility.INTERMEDIATE).toBe(true);
  });

  it('모든 필터를 초기화한다', () => {
    const { setSearchQuery, setSortBy, setSortDirection, setSelectedTagId, clearFilters } = useTagDashboardSidebarStore.getState();

    // 여러 상태 변경
    setSearchQuery('테스트');
    setSortBy('name');
    setSortDirection('desc');
    setSelectedTagId(999);

    const beforeClear = useTagDashboardSidebarStore.getState();
    expect(beforeClear.searchQuery).toBe('테스트');
    expect(beforeClear.sortBy).toBe('name');
    expect(beforeClear.sortDirection).toBe('desc');
    expect(beforeClear.selectedTagId).toBe(999);

    // 필터 초기화
    clearFilters();

    const afterClear = useTagDashboardSidebarStore.getState();
    expect(afterClear.searchQuery).toBe('');
    expect(afterClear.sortBy).toBe('progress');
    expect(afterClear.sortDirection).toBe('asc');
    expect(afterClear.selectedTagId).toBeNull();
    expect(afterClear.categoryVisibility).toEqual({
      INTERMEDIATE: true,
      ADVANCED: true,
      MASTER: false,
      LOCKED: true,
      EXCLUDED: false,
    });
  });
});
