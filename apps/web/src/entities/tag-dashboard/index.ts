export type { TagDashboard, TagBan, CategoryTags, Categories, CategoryInfoTags, TagDetail, TagDetailProblem, TagDetailTag } from './model/tagDashboard.types';
export { tagDashboardApi } from './api/tagDashboard.api';
export { useTagDashboard, usePostTagBan, useDeleteTagBan, useTagDetail } from './model/queries';
