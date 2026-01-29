import { useLandingTagDashboard } from '@/features/landing';
import { TagDashboard } from '@/features/tag-dashboard';

export default function LandingMainTagDashboard() {
  const tagDashboard = useLandingTagDashboard();
  return (
    <div className="bg-innerground-white flex h-full w-full flex-col p-4">
      <div className="relative min-h-0 flex-1">
        <TagDashboard tagDashboard={tagDashboard} isLanding={true} />
      </div>
    </div>
  );
}
