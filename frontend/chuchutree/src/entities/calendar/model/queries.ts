'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { calendarApi } from '../api/calendar.api';
import { UpdateProblemsData } from './types';

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

// Will Solve 문제 업데이트 mutation
export const useUpdateWillSolveProblems = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: UpdateProblemsData) => calendarApi.updateWillSolveProblems(data),
    onSuccess: (_, variables) => {
      // 해당 날짜가 포함된 월의 캐시 무효화
      const date = new Date(variables.date);
      const year = date.getFullYear();
      const month = date.getMonth() + 1;
      queryClient.invalidateQueries({ queryKey: calendarKeys.list(year, month) });
    },
  });
};

// Solved 문제 업데이트 mutation
export const useUpdateSolvedProblems = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: UpdateProblemsData) => calendarApi.updateSolvedProblems(data),
    onSuccess: (_, variables) => {
      // 해당 날짜가 포함된 월의 캐시 무효화
      const date = new Date(variables.date);
      const year = date.getFullYear();
      const month = date.getMonth() + 1;
      queryClient.invalidateQueries({ queryKey: calendarKeys.list(year, month) });
    },
  });
};
