import { useOnboardingStore } from '../onboarding';

describe('OnboardingStore', () => {
  beforeEach(() => {
    // 각 테스트 전 store 초기화
    useOnboardingStore.setState({
      hasCompletedOnboarding: false,
      isActive: false,
      currentStep: 1,
      _hasHydrated: false,
    });
  });

  it('초기 상태가 올바르게 설정된다', () => {
    const state = useOnboardingStore.getState();

    expect(state.hasCompletedOnboarding).toBe(false);
    expect(state.isActive).toBe(false);
    expect(state.currentStep).toBe(1);
    expect(state._hasHydrated).toBe(false);
  });

  it('온보딩을 시작한다', () => {
    const { startOnboarding } = useOnboardingStore.getState();

    startOnboarding();

    const state = useOnboardingStore.getState();
    expect(state.isActive).toBe(true);
    expect(state.currentStep).toBe(1);
  });

  it('다음 단계로 이동한다', () => {
    const { startOnboarding, nextStep } = useOnboardingStore.getState();

    startOnboarding();
    nextStep();

    expect(useOnboardingStore.getState().currentStep).toBe(2);

    nextStep();
    expect(useOnboardingStore.getState().currentStep).toBe(3);
  });

  it('중간 단계에서 skip하면 다음 단계로 이동한다', () => {
    const { startOnboarding, skipCurrentStep } = useOnboardingStore.getState();

    startOnboarding();

    // step 1에서 skip
    skipCurrentStep();
    expect(useOnboardingStore.getState().currentStep).toBe(2);

    // step 2에서 skip
    skipCurrentStep();
    expect(useOnboardingStore.getState().currentStep).toBe(3);

    // 온보딩은 아직 완료되지 않음
    expect(useOnboardingStore.getState().hasCompletedOnboarding).toBe(false);
    expect(useOnboardingStore.getState().isActive).toBe(true);
  });

  it('마지막 단계(step 8)에서 skip하면 온보딩이 완료된다', () => {
    const { startOnboarding, skipCurrentStep } = useOnboardingStore.getState();

    startOnboarding();

    // step 8로 이동
    useOnboardingStore.setState({ currentStep: 8 });

    // step 8에서 skip
    skipCurrentStep();

    const state = useOnboardingStore.getState();
    expect(state.hasCompletedOnboarding).toBe(true);
    expect(state.isActive).toBe(false);
    expect(state.currentStep).toBe(1);
  });

  it('온보딩을 완료한다', () => {
    const { startOnboarding, completeOnboarding } = useOnboardingStore.getState();

    startOnboarding();
    useOnboardingStore.setState({ currentStep: 5 });

    completeOnboarding();

    const state = useOnboardingStore.getState();
    expect(state.hasCompletedOnboarding).toBe(true);
    expect(state.isActive).toBe(false);
    expect(state.currentStep).toBe(1);
  });

  it('온보딩을 재시작한다', () => {
    const { completeOnboarding, resetOnboarding } = useOnboardingStore.getState();

    // 온보딩 완료
    completeOnboarding();
    expect(useOnboardingStore.getState().hasCompletedOnboarding).toBe(true);

    // 재시작
    resetOnboarding();

    const state = useOnboardingStore.getState();
    expect(state.hasCompletedOnboarding).toBe(false);
    expect(state.isActive).toBe(false);
    expect(state.currentStep).toBe(1);
  });
});
