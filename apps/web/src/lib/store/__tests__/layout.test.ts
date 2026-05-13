import { useLayoutStore } from '../layout';

describe('LayoutStore', () => {
  beforeEach(() => {
    // 각 테스트 전 store 초기화
    useLayoutStore.setState({
      topSection: null,
      centerSection: 'calendar',
      bottomSection: null,
      infoSidebarWidth: 280,
      topSectionTierbarHeight: 120,
      topSectionStreakHeight: 240,
      bottomSectionHeight: 240,
      isResizing: false,
    });
  });

  it('초기 상태가 올바르게 설정된다', () => {
    const state = useLayoutStore.getState();

    expect(state.topSection).toBeNull();
    expect(state.centerSection).toBe('calendar');
    expect(state.bottomSection).toBeNull();
  });

  it('top section을 토글한다 (같은 버튼 클릭 시 닫기)', () => {
    const { toggleTopSection } = useLayoutStore.getState();

    // tierbar 열기
    toggleTopSection('tierbar');
    expect(useLayoutStore.getState().topSection).toBe('tierbar');

    // 같은 버튼 클릭 시 닫기
    toggleTopSection('tierbar');
    expect(useLayoutStore.getState().topSection).toBeNull();
  });

  it('tierbar에서 streak으로 전환한다', () => {
    const { toggleTopSection } = useLayoutStore.getState();

    // tierbar 열기
    toggleTopSection('tierbar');
    expect(useLayoutStore.getState().topSection).toBe('tierbar');

    // streak으로 전환
    toggleTopSection('streak');
    expect(useLayoutStore.getState().topSection).toBe('streak');
  });

  it('center section을 전환한다', () => {
    const { setCenterSection } = useLayoutStore.getState();

    setCenterSection('dashboard');
    expect(useLayoutStore.getState().centerSection).toBe('dashboard');

    setCenterSection('calendar');
    expect(useLayoutStore.getState().centerSection).toBe('calendar');
  });

  it('bottom section을 토글한다', () => {
    const { toggleBottomSection } = useLayoutStore.getState();

    // recommend 열기
    toggleBottomSection();
    expect(useLayoutStore.getState().bottomSection).toBe('recommend');

    // recommend 닫기
    toggleBottomSection();
    expect(useLayoutStore.getState().bottomSection).toBeNull();
  });

  it('topSection을 열면 bottomSection이 닫힌다', () => {
    const { toggleTopSection, toggleBottomSection } = useLayoutStore.getState();

    // bottomSection을 'recommend'로 설정
    toggleBottomSection();
    expect(useLayoutStore.getState().bottomSection).toBe('recommend');

    // topSection을 'tierbar'로 설정
    toggleTopSection('tierbar');

    const state = useLayoutStore.getState();
    expect(state.topSection).toBe('tierbar');
    expect(state.bottomSection).toBeNull();
  });

  it('bottomSection을 열면 topSection이 닫힌다', () => {
    const { toggleTopSection, toggleBottomSection } = useLayoutStore.getState();

    // topSection을 'tierbar'로 설정
    toggleTopSection('tierbar');
    expect(useLayoutStore.getState().topSection).toBe('tierbar');

    // bottomSection을 'recommend'로 설정
    toggleBottomSection();

    const state = useLayoutStore.getState();
    expect(state.bottomSection).toBe('recommend');
    expect(state.topSection).toBeNull();
  });
});
