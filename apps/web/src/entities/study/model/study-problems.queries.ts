'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { studyProblemsApi } from '../api/study-problems.api';
import { studyProblemsKeys } from './study-problems.keys';
import { AssignAllProblemsRequest, AssignIndividualProblemsRequest } from './study-problems.types';
import { UseMutationCallback } from '@/shared/types/api';

// ── 스터디 문제 조회 (월간) ──────────────────────────────────────

export const useStudyProblems = (studyId: number, year: number, month: number) => {
  return useQuery({
    queryKey: studyProblemsKeys.list(studyId, year, month),
    queryFn: () => studyProblemsApi.getStudyProblems(studyId, year, month),
    enabled: studyId > 0,
  });
};

// ── 전원 문제 할당 ───────────────────────────────────────────────

export const useAssignProblemAll = (studyId: number, callbacks?: UseMutationCallback) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (body: AssignAllProblemsRequest) => studyProblemsApi.assignProblemToAll(studyId, body),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: studyProblemsKeys.lists() });
      callbacks?.onSuccess?.();
    },
    onError: (error) => callbacks?.onError?.(error),
  });
};

// ── 개인별 문제 할당 ─────────────────────────────────────────────

export const useAssignProblemIndividual = (studyId: number, callbacks?: UseMutationCallback) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (body: AssignIndividualProblemsRequest) => studyProblemsApi.assignProblemToIndividuals(studyId, body),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: studyProblemsKeys.lists() });
      callbacks?.onSuccess?.();
    },
    onError: (error) => callbacks?.onError?.(error),
  });
};

// ── 문제 할당 삭제 ───────────────────────────────────────────────

export const useDeleteStudyProblem = (studyId: number, callbacks?: UseMutationCallback) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (studyProblemId: number) => studyProblemsApi.deleteStudyProblem(studyId, studyProblemId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: studyProblemsKeys.lists() });
      callbacks?.onSuccess?.();
    },
    onError: (error) => callbacks?.onError?.(error),
  });
};
