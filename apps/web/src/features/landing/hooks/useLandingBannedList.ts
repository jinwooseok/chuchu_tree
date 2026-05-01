import bannedListMockData from '../mock/user-accounts_me_problems_banned-list_260126.json';
import { BannedProblems } from '@/entities/recommendation';

export function useLandingBannedList() {
  return bannedListMockData.data as BannedProblems;
}
