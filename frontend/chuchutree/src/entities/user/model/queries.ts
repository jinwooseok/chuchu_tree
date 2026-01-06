'use client';

import { useQuery } from '@tanstack/react-query';
import { userApi } from '../api/user.api';

export const userKeys = {
  all: ['user'],
  me: () => [...userKeys.all, 'me'],
};

export const useUser = () => {
  return useQuery({
    queryKey: userKeys.me(),
    queryFn: userApi.getMe,
    staleTime: 5 * 60 * 1000,
  });
};
