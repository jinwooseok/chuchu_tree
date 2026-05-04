import { TagSidebarInset } from '@/features/tag-dashboard';
import { useLandingTagDashboard } from '@/features/landing';

export default function LandingTagSidebar() {
  const tagDashboard = useLandingTagDashboard();
  return <TagSidebarInset tagDashboard={tagDashboard} isLanding={true} />;
}
