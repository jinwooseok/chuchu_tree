'use client';

import { useQuery } from '@tanstack/react-query';
import { calendarApi } from '../api/calendar.api';

export const calendarKeys = {
  all: ['calendar'],
  lists: () => [...calendarKeys.all, 'list'],
  list: (year: number, month: number) => [...calendarKeys.lists(), { year, month }],
};

export const useCalendar = (year: number, month: number) => {
  return useQuery({
    queryKey: calendarKeys.list(year, month),
    queryFn: () => calendarApi.getCalendar({ year, month }),
    staleTime: 5 * 60 * 1000,
  });
};
