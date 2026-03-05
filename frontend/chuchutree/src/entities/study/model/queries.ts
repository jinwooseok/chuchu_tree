'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { studyApi } from '../api/study.api';
import { studyKeys } from './keys';
import { CreateStudyRequest } from './types';
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
