import { serverFetch } from '@/lib/server';
import { User } from '../model/types';

export const userServerApi = {
  getMe: () => serverFetch<User>('bj-accounts/me'),
};
