import { serverFetch } from '@/lib/server';
import { Calendar } from '../model/types';

export const calendarServerApi = {
  getCalendar: ({ year, month }: { year: number; month: number }) => serverFetch<Calendar>(`bj-accounts/me/problems?year=${year}&month=${month}`),
};
