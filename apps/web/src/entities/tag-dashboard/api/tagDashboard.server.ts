import { serverFetch } from '@/lib/server';
import { TagDashboard } from '../model/tagDashboard.types';

export const TagDashboardServerApi = {
  getTagDashboard: () => serverFetch<TagDashboard>(`user-accounts/me/tags`),
};
