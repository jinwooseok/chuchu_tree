'use client';

import { useQuery } from '@tanstack/react-query';
import { userApi } from '../api/user.api';

export const userKeys = {
  all: ['user'],
  me: () => [...userKeys.all, 'me'],
  detail: (userId: string) => [...userKeys.all, userId],
};

export const useUser = () => {
  return useQuery({
    queryKey: userKeys.me(),
    queryFn: userApi.getMe,
    staleTime: 5 * 60 * 1000,
  });
};

export const useUserById = (id: string) => {
  return useQuery({
    queryKey: userKeys.detail(id),
    queryFn: () => userApi.getUserById(id),
  });
};
