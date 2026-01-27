import { Calendar } from '@/entities/calendar';
import calendarData1 from '../mock/bj-accounts_me_problems_25_12_260126.json';
import calendarData2 from '../mock/bj-accounts_me_problems_26_01_260126.json';
import calendarData3 from '../mock/bj-accounts_me_problems_26_02_260126.json';

export function useLandingCalendar() {
  return calendarData1.data as Calendar;
}
