import { RefreshButtonContainer } from '@/features/refresh';
import { StudyDashboard } from '@/features/study';
import { useStudyDetail, useStudyProblems } from '@/entities/study';
import { useUser } from '@/entities/user';
import { useStudyCalendarStore } from '@/lib/store/studyCalendar';
import dynamic from 'next/dynamic';
import { useEffect, useState } from 'react';

// 클라이언트 전용 렌더링 (hydration mismatch 방지)
const StudyBigCalendar = dynamic(() => import('@/features/study').then((mod) => mod.StudyBigCalendar), {
  ssr: false,
  loading: () => (
    <div className="flex h-full w-full items-center justify-center">
      <div className="text-sm text-gray-400">Loading...</div>
    </div>
  ),
});

export default function MainStudy({ studyName }: { studyName: string }) {
  const studyId = Number(studyName);
  const { data: studyDetail, isLoading, isError } = useStudyDetail(studyId);
  const { data: user } = useUser();
  const { bigCalendarDate, setBigCalendarDate } = useStudyCalendarStore();
  const [initialDate] = useState(new Date());

  // 컴포넌트 마운트 시 bigCalendarDate가 null이면 초기 날짜로 설정
  useEffect(() => {
    if (!bigCalendarDate) {
      setBigCalendarDate(initialDate);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const currentDate = bigCalendarDate || initialDate;
  const year = currentDate.getFullYear();
  const month = currentDate.getMonth() + 1;
  const { data: studyCalendarData } = useStudyProblems(studyId, year, month);

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
        <div className="relative w-full" style={{ minHeight: '500px' }}>
          <StudyBigCalendar studyCalendarData={studyCalendarData} />
        </div>
        {/* 하단 문제추천영역 */}
        {/* 하단 문제추천 history 영역 */}
        <RefreshButtonContainer />
      </div>
    </div>
  );
}
