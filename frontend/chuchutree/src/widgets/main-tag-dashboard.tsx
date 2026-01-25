import { RefreshButtonContainer } from '@/features/refresh';
import TagDashboard from '@/features/tag-dashboard/ui/TagDashboard';

export default function MainTagDashboard() {
  return (
    <div className="bg-innerground-white flex h-full w-full flex-col p-4">
      <div className="relative min-h-0 flex-1">
        <TagDashboard />
        <RefreshButtonContainer />
      </div>
    </div>
  );
}
