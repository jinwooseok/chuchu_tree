import { RefreshButtonContainer } from '@/features/refresh';
import { StudyDashboard } from '@/features/study';

export default function MainStudy({ studyName }: { studyName: string }) {
  const studyInfo = 'temp data';
  return (
    <div className="bg-innerground-white flex h-full w-full flex-col p-4">
      <div className="relative min-h-0 flex-1">
        <StudyDashboard studyInfo={studyInfo} />
        <RefreshButtonContainer />
      </div>
    </div>
  );
}
