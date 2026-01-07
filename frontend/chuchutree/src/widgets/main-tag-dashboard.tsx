import RefreshButton from '@/features/refresh/ui/RefreshButton';
import TagDashboard from '@/features/tag-dashboard/ui/TagDashboard';

export default function MainTagDashboard() {
  return (
    <div className="bg-innerground-white flex h-full w-full flex-col p-4">
      <div className="relative min-h-0 flex-1">
        <TagDashboard />
        <div className="absolute right-16 bottom-16">
          <RefreshButton />
        </div>
      </div>
    </div>
  );
}
