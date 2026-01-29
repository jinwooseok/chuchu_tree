import { User } from '@/entities/user';
import userMockData from '../mock/bj-accounts_me_260126.json';

export function useLandingUser() {
  return userMockData.data as User;
}
