import { TagSidebarInset } from '@/features/tag-dashboard';
import { useTagDashboard } from '@/entities/tag-dashboard';

export default function TagSidebar() {
  const { data: tagDashboard } = useTagDashboard();
  return <TagSidebarInset tagDashboard={tagDashboard}/>;
}
