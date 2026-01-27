import tagDashboardMockData from '../mock/user-accounts_me_tags_260126.json';
import { TagDashboard } from '@/entities/tag-dashboard';

export function useLandingTagDashboard() {
  return tagDashboardMockData.data as TagDashboard;
}
