'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { calendarApi } from '../api/calendar.api';
import { UpdateProblemsData } from './calendar.types';
import { UseMutationCallback } from '@/shared/types/api';
import { calendarKeys } from './keys';

export const useCalendar = (year: number, month: number) => {
  return useQuery({
    queryKey: calendarKeys.list(year, month),
    queryFn: () => calendarApi.getCalendar({ year, month }),
  });
};

// 문제 검색
export const useSearchProblems = (keyword: string) => {
  return useQuery({
    queryKey: calendarKeys.search(keyword),
    queryFn: () => calendarApi.getSearchProblems({ keyword }),
    enabled: keyword.trim().length > 0, // 키워드가 있을 때만 요청
    staleTime: Infinity, // 공격적 캐싱
    gcTime: 60 * 60 * 1000, // 공격적 캐싱
    refetchOnWindowFocus: false, // 공격적 캐싱
    refetchOnMount: false, // 공격적 캐싱
  });
};

// Will Solve 문제 업데이트 mutation
export const useUpdateWillSolveProblems = (callbacks?: UseMutationCallback) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: UpdateProblemsData) => calendarApi.updateWillSolveProblems(data),
    onSuccess: (_, variables) => {
      // 해당 날짜가 포함된 월의 캐시 무효화
      const date = new Date(variables.date);
      const year = date.getFullYear();
      const month = date.getMonth() + 1;
      queryClient.invalidateQueries({ queryKey: calendarKeys.list(year, month) });
      if (callbacks?.onSuccess) callbacks.onSuccess();
    },
    onError: (error) => {
      if (callbacks?.onError) callbacks.onError(error);
    },
  });
};

// Solved 문제 업데이트 mutation
export const useUpdateSolvedProblems = (callbacks?: UseMutationCallback) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: UpdateProblemsData) => calendarApi.updateSolvedProblems(data),
    onSuccess: (_, variables) => {
      // 해당 날짜가 포함된 월의 캐시 무효화
      const date = new Date(variables.date);
      const year = date.getFullYear();
      const month = date.getMonth() + 1;
      queryClient.invalidateQueries({ queryKey: calendarKeys.list(year, month) });
      if (callbacks?.onSuccess) callbacks.onSuccess();
    },
    onError: (error) => {
      if (callbacks?.onError) callbacks.onError(error);
    },
  });
};
