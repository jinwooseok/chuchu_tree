'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { calendarApi } from '../api/calendar.api';
import type { UpdateProblemsData, Calendar } from './calendar.types';
import { UseMutationCallback } from '@/shared/types/api';
import { calendarKeys } from './keys';
import '@/shared/types/query';

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
    onMutate: async (variables) => {
      const date = new Date(variables.date);
      const year = date.getFullYear();
      const month = date.getMonth() + 1;
      const queryKey = calendarKeys.list(year, month);

      // 진행 중인 쿼리 취소
      await queryClient.cancelQueries({ queryKey });

      // 이전 데이터 저장
      const previousData = queryClient.getQueryData(queryKey);

      // 낙관적 업데이트
      queryClient.setQueryData(queryKey, (old: Calendar) => {
        if (!old) return old;

        return {
          ...old,
          monthlyData: old.monthlyData.map((day) => {
            if (day.targetDate === variables.date) {
              // 기존 문제 + 새 문제 병합
              const existingProblems = day.willSolveProblems || [];
              const newProblemsMap = new Map((variables.newProblems || []).map((p) => [p.problemId, p]));
              const allProblemsMap = new Map(existingProblems.map((p) => [p.problemId, p]));

              // 새 문제 추가
              newProblemsMap.forEach((problem, id) => {
                allProblemsMap.set(id, problem);
              });

              // willSolveProblems를 업데이트된 순서로 재구성
              const newWillSolveProblems = variables.problemIds.map((id) => allProblemsMap.get(id)).filter(Boolean);

              return {
                ...day,
                willSolveProblems: newWillSolveProblems,
                willSolveProblemCount: newWillSolveProblems.length,
              };
            }
            return day;
          }),
        };
      });

      return { previousData, queryKey };
    },
    onError: (error, _, context) => {
      // 롤백
      if (context?.previousData) {
        queryClient.setQueryData(context.queryKey, context.previousData);
      }
      if (callbacks?.onError) callbacks.onError(error);
    },
    onSettled: (_, __, variables) => {
      // 서버 데이터와 동기화
      const date = new Date(variables.date);
      const year = date.getFullYear();
      const month = date.getMonth() + 1;
      queryClient.invalidateQueries({ queryKey: calendarKeys.list(year, month) });
    },
    onSuccess: () => {
      if (callbacks?.onSuccess) callbacks.onSuccess();
    },
  });
};

// Solved 문제 업데이트 mutation
export const useUpdateSolvedProblems = (callbacks?: UseMutationCallback) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: UpdateProblemsData) => calendarApi.updateSolvedProblems(data),
    onMutate: async (variables) => {
      const date = new Date(variables.date);
      const year = date.getFullYear();
      const month = date.getMonth() + 1;
      const queryKey = calendarKeys.list(year, month);

      // 진행 중인 쿼리 취소
      await queryClient.cancelQueries({ queryKey });

      // 이전 데이터 저장
      const previousData = queryClient.getQueryData(queryKey);

      // 낙관적 업데이트
      queryClient.setQueryData(queryKey, (old: Calendar) => {
        if (!old) return old;

        return {
          ...old,
          monthlyData: old.monthlyData.map((day) => {
            if (day.targetDate === variables.date) {
              // solvedProblems를 업데이트된 순서로 재구성
              const newSolvedProblems = variables.problemIds.map((id) => day.solvedProblems.find((p) => p.problemId === id)).filter(Boolean);

              return {
                ...day,
                solvedProblems: newSolvedProblems,
              };
            }
            return day;
          }),
        };
      });

      return { previousData, queryKey };
    },
    onError: (error, _, context) => {
      // 롤백
      if (context?.previousData) {
        queryClient.setQueryData(context.queryKey, context.previousData);
      }
      if (callbacks?.onError) callbacks.onError(error);
    },
    onSettled: (_, __, variables) => {
      // 서버 데이터와 동기화
      const date = new Date(variables.date);
      const year = date.getFullYear();
      const month = date.getMonth() + 1;
      queryClient.invalidateQueries({ queryKey: calendarKeys.list(year, month) });
    },
    onSuccess: () => {
      if (callbacks?.onSuccess) callbacks.onSuccess();
    },
  });
};
