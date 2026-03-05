import { RefreshButtonContainer } from '@/features/refresh';
import { StudyDashboard } from '@/features/study';
import { useStudyDetail } from '@/entities/study';
import { useUser } from '@/entities/user';

export default function MainStudy({ studyName }: { studyName: string }) {
  const studyId = Number(studyName);
  const { data: studyDetail, isLoading, isError } = useStudyDetail(studyId);
  const { data: user } = useUser();

  if (isLoading) {
    return (
      <div className="bg-innerground-white flex h-full w-full items-center justify-center p-4">
        <p className="text-muted-foreground text-sm">로딩 중...</p>
      </div>
    );
  }

  if (isError || !studyDetail) {
    return (
      <div className="bg-innerground-white flex h-full w-full items-center justify-center p-4">
        <p className="text-muted-foreground text-sm">스터디 정보를 불러올 수 없습니다.</p>
      </div>
    );
  }

  return (
    <div className="bg-innerground-white flex h-full w-full flex-col p-4">
      <div className="relative min-h-0 flex-1">
        <StudyDashboard studyDetail={studyDetail} currentUserAccountId={user?.userAccount?.userAccountId ?? 0} />
        <RefreshButtonContainer />
      </div>
    </div>
  );
}
