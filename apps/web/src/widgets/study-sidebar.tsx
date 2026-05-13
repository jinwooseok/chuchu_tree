import { useStudyDetail, useStudyProblems } from '@/entities/study';
import { StudySidebarInset } from '@/features/study';
import { useStudyCalendarStore } from '@/lib/store/studyCalendar';
import { useLayoutStore } from '@/lib/store/layout';
import dynamic from 'next/dynamic';
import { useState, useEffect } from 'react';
import { isSameMonth } from 'date-fns';

// 클라이언트 전용 렌더링 (hydration mismatch 방지)
const StudySmallCalendar = dynamic(() => import('@/features/study').then((mod) => mod.StudySmallCalendar), {
  ssr: false,
  loading: () => (
    <div className="flex items-center justify-center" style={{ minHeight: '300px' }}>
      <div className="text-sm text-gray-400">Loading...</div>
    </div>
  ),
});

export default function StudySidebar() {
  const { studySection } = useLayoutStore();
  const studyId = Number(studySection);

  const { bigCalendarDate } = useStudyCalendarStore();

  // SmallCalendar의 현재 표시 월 관리
  const [activeStartDate, setActiveStartDate] = useState<Date>(bigCalendarDate || new Date());

  // BigCalendar의 월이 변경되면 SmallCalendar도 따라감
  useEffect(() => {
    if (bigCalendarDate && !isSameMonth(bigCalendarDate, activeStartDate)) {
      setActiveStartDate(bigCalendarDate);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [bigCalendarDate]); // activeStartDate 제거 (무한 루프 방지)

  // activeStartDate 기준으로 데이터 fetch
  const year = activeStartDate.getFullYear();
  const month = activeStartDate.getMonth() + 1;
  const { data: studyCalendarData } = useStudyProblems(studyId, year, month);
  const { data: studyDetail } = useStudyDetail(studyId);

  return (
    <div className="hide-scrollbar flex h-full flex-col gap-8 overflow-y-auto p-4">
      <StudySmallCalendar studyCalendarData={studyCalendarData} activeStartDate={activeStartDate} onActiveStartDateChange={setActiveStartDate} />
      <StudySidebarInset studyCalendarData={studyCalendarData} studyDetail={studyDetail} studyId={studyId} />
    </div>
  );
}
