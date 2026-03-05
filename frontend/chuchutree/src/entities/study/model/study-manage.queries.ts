'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { studyApi } from '../api/study-manage.api';
import { studyKeys } from './study-manage.keys';
import { CreateStudyRequest } from './study-manage.types';
import { UseMutationCallback } from '@/shared/types/api';

export const useMyStudies = () => {
  return useQuery({
    queryKey: studyKeys.myList(),
    queryFn: studyApi.getMyStudies,
  });
};

export const useValidateStudyName = () => {
  return useMutation({
    mutationFn: (name: string) => studyApi.validateStudyName(name),
  });
};

export const useSearchUsers = (keyword: string) => {
  return useQuery({
    queryKey: studyKeys.searchUsers(keyword),
    queryFn: () => studyApi.searchUsers(keyword),
    enabled: keyword.length > 0,
  });
};

export const useSearchStudies = (keyword: string) => {
  return useQuery({
    queryKey: studyKeys.searchStudies(keyword),
    queryFn: () => studyApi.searchStudies(keyword),
    enabled: keyword.length > 0,
  });
};

export const useApplyStudy = (callbacks?: UseMutationCallback) => {
  return useMutation({
    mutationFn: (studyId: number) => studyApi.applyStudy(studyId),
    onSuccess: () => callbacks?.onSuccess?.(),
    onError: (error) => callbacks?.onError?.(error),
  });
};

export const useCancelApplyStudy = (callbacks?: UseMutationCallback) => {
  return useMutation({
    mutationFn: (studyId: number) => studyApi.cancelApplyStudy(studyId),
    onSuccess: () => callbacks?.onSuccess?.(),
    onError: (error) => callbacks?.onError?.(error),
  });
};

export const useCreateStudy = (callbacks?: UseMutationCallback) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (body: CreateStudyRequest) => studyApi.createStudy(body),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: studyKeys.myList() });
      callbacks?.onSuccess?.();
    },
    onError: (error) => {
      callbacks?.onError?.(error);
    },
  });
};
