import { TagDashboard } from '@/features/tag-dashboard';
import { RefreshButtonContainer } from '@/features/refresh';
import { useTagDashboard } from '@/entities/tag-dashboard';

export default function MainTagDashboard() {
  const { data: tagDashboard } = useTagDashboard();
  return (
    <div className="bg-innerground-white flex h-full w-full flex-col p-4">
      <div className="relative min-h-0 flex-1">
        <TagDashboard tagDashboard={tagDashboard}/>
        <RefreshButtonContainer />
      </div>
    </div>
  );
}
