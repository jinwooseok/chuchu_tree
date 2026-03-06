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
      <div className="hide-scrollbar relative flex min-h-0 flex-1 flex-col items-center space-y-4 overflow-y-auto">
        {/* 상단 기본정보 및 모달 영역 */}
        <StudyDashboard studyDetail={studyDetail} currentUserAccountId={user?.userAccount?.userAccountId ?? 0} />
        {/* 중앙 캘린더영역 */}
        {/* 하단 문제추천영역 */}
        {/* 하단 문제추천 history 영역 */}
        <RefreshButtonContainer />
      </div>
    </div>
  );
}
