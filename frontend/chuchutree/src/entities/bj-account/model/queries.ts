'use client';

import { useMutation } from '@tanstack/react-query';
import { baekjoonApi } from '../api/bj.api';
import { LinkBjAccountRequest } from './types';

export const baekjoonKeys = {
  all: ['baekjoon'],
  link: () => [...baekjoonKeys.all, 'link'],
};

export const useLinkBjAccount = () => {
  return useMutation({
    mutationFn: (data: LinkBjAccountRequest) => baekjoonApi.linkAccount(data),
  });
};
export const usePatchBjAccount = () => {
  return useMutation({
    mutationFn: (data: LinkBjAccountRequest) => baekjoonApi.patchAccount(data),
  });
};
