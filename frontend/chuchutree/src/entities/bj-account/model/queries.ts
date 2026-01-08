'use client';

import { useMutation } from '@tanstack/react-query';
import { baekjoonApi } from '../api/bj.api';
import { LinkBjAccountRequest } from './types';
import { UseMutationCallback } from '@/shared/types/api';

export const baekjoonKeys = {
  all: ['baekjoon'],
  link: () => [...baekjoonKeys.all, 'link'],
};

export const useLinkBjAccount = (callbacks: UseMutationCallback) => {
  return useMutation({
    mutationFn: (data: LinkBjAccountRequest) => baekjoonApi.linkAccount(data),
    onSuccess: () => {
      if (callbacks.onSuccess) callbacks.onSuccess();
    },
    onError: (error) => {
      if (callbacks.onError) callbacks.onError(error);
    },
  });
};
export const usePatchBjAccount = (callbacks: UseMutationCallback) => {
  return useMutation({
    mutationFn: (data: LinkBjAccountRequest) => baekjoonApi.patchAccount(data),
    onSuccess: () => {
      if (callbacks.onSuccess) callbacks.onSuccess();
    },
    onError: (error) => {
      if (callbacks.onError) callbacks.onError(error);
    },
  });
};
