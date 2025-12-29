import { serverFetch } from '@/lib/server';
import { User } from '../model/types';

export const userServerApi = {
  getMe: () => serverFetch<User>('/api/user'),
  getUserById: (id: string) => serverFetch<User>(`/api/user/${id}`),
};
