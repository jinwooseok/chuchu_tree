import { useCalendarStore } from '../calendar';

describe('CalendarStore', () => {
  beforeEach(() => {
    // 각 테스트 전 store 초기화
    useCalendarStore.setState({
      selectedDate: new Date(),
      bigCalendarDate: new Date(),
    });
  });

  it('초기 상태가 현재 날짜로 설정된다', () => {
    const state = useCalendarStore.getState();

    expect(state.selectedDate).toBeInstanceOf(Date);
    expect(state.bigCalendarDate).toBeInstanceOf(Date);
  });

  it('selectedDate와 BigCalendarDate를 설정한다', () => {
    const testDate = new Date('2025-01-15');
    const { setSelectedDate, setBigCalendarDate } = useCalendarStore.getState();

    setSelectedDate(testDate);
    expect(useCalendarStore.getState().selectedDate).toEqual(testDate);

    setBigCalendarDate(testDate);
    expect(useCalendarStore.getState().bigCalendarDate).toEqual(testDate);
  });

  it('큰 캘린더 날짜를 설정한다', () => {
    const testDate = new Date('2025-02-01');
    const { setBigCalendarDate } = useCalendarStore.getState();

    setBigCalendarDate(testDate);
    expect(useCalendarStore.getState().bigCalendarDate).toEqual(testDate);
  });
});
