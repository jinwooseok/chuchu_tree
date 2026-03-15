'use client';

import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { useNotificationStore } from '@/lib/store/notification';
import { useState, useEffect } from 'react';
import { Bell, Loader2 } from 'lucide-react';
import { BaseNotice, RequestedStudyApplicationContent, useNotices, useReadNotices } from '@/entities/notice';
import { ANNOUNCEMENT_CATEGORIES, PERSONAL_CATEGORIES, STUDY_CATEGORIES, NoticeTab } from '../model/notice.constants';
import { NoticeCard } from './NoticeCard';
import { useModal } from '@/lib/providers/modal-provider';
import { useLayoutStore } from '@/lib/store/layout';
import { CreateStudyDialog } from '@/features/sidebar/ui/group-study/CreateStudyDialog';

interface Props {
  onClose: () => void;
}

export function NoticeDialog({ onClose }: Props) {
  const { setHasUnread, setPendingStudyInviteAction } = useNotificationStore();
  const { openModal, closeModal } = useModal();
  const { setStudySection } = useLayoutStore();
  const [activeTab, setActiveTab] = useState<NoticeTab>('study');

  const { data: notices = [], isLoading, isError } = useNotices();
  const { mutate: readNotices } = useReadNotices();

  // 최신순 정렬
  const sortedNotices = [...notices].sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime());

  // 모달 오픈 시 unread 스냅샷 — dot 표시 기준
  const [initiallyUnreadIds] = useState<Set<number>>(() => new Set<number>());

  useEffect(() => {
    if (notices.length === 0) return;
    const unreadIds = notices.filter((n) => !n.isRead).map((n) => n.noticeId);
    unreadIds.forEach((id) => initiallyUnreadIds.add(id));
    setHasUnread(false);
    if (unreadIds.length > 0) {
      readNotices(unreadIds);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [notices.length > 0]);

  const handleGoToDetail = (notice: BaseNotice) => {
    if (notice.categoryDetail === 'REQUESTED_STUDY_INVITATION') {
      // CreateStudyDialog의 신청/초대기록 탭 열기
      onClose();
      openModal('create-study', <CreateStudyDialog defaultTab="records" onClose={() => closeModal('create-study')} />);
    } else if (notice.categoryDetail === 'REQUESTED_STUDY_APPLICATION') {
      // 해당 스터디로 이동 후 StudyInviteDialog received 탭 자동 열기 신호
      const content = notice.content as RequestedStudyApplicationContent;
      setStudySection(content.studyId.toString());
      setPendingStudyInviteAction({ studyId: content.studyId, tab: 'received' });
      onClose();
    }
  };

  const tabCategories = activeTab === 'study' ? STUDY_CATEGORIES : activeTab === 'personal' ? PERSONAL_CATEGORIES : ANNOUNCEMENT_CATEGORIES;
  const filteredNotices = sortedNotices.filter((n) => tabCategories.includes(n.category));

  return (
    <Dialog open={true} onOpenChange={onClose}>
      <DialogContent className="flex h-[80vh] max-w-xl flex-col">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Bell className="h-4 w-4" />
            알림
          </DialogTitle>
          <DialogDescription className="sr-only">스터디 알림, 개인 알림, 공지사항을 확인할 수 있습니다.</DialogDescription>
        </DialogHeader>

        {/* 탭 전환 */}
        <div className="flex border-b">
          {(['study', 'personal', 'announcement'] as NoticeTab[]).map((tab) => (
            <button
              key={tab}
              className={`flex-1 py-2 text-sm font-medium transition-colors ${activeTab === tab ? 'border-primary text-foreground border-b-2' : 'text-muted-foreground hover:text-foreground'}`}
              onClick={() => setActiveTab(tab)}
            >
              {tab === 'study' ? '스터디 알림' : tab === 'personal' ? '내 알림' : '공지사항'}
            </button>
          ))}
        </div>

        {isLoading ? (
          <div className="flex min-h-48 flex-col items-center justify-center gap-2">
            <Loader2 className="text-muted-foreground h-6 w-6 animate-spin" />
          </div>
        ) : isError ? (
          <div className="flex min-h-48 flex-col items-center justify-center gap-2">
            <p className="text-muted-foreground text-sm">알림을 불러오지 못했습니다.</p>
          </div>
        ) : filteredNotices.length > 0 ? (
          <div className="min-h-0 flex-1 overflow-y-auto pt-2 pr-1">
            <div className="space-y-2">
              {filteredNotices.map((notice) => (
                <NoticeCard
                  key={notice.noticeId}
                  notice={notice}
                  showUnreadDot={initiallyUnreadIds.has(notice.noticeId)}
                  onGoToDetail={handleGoToDetail}
                />
              ))}
            </div>
          </div>
        ) : (
          <div className="flex min-h-48 flex-col items-center justify-center gap-2">
            <Bell className="text-muted-foreground h-8 w-8 opacity-30" />
            <p className="text-muted-foreground text-sm">새로운 알림이 없습니다.</p>
          </div>
        )}

        <div className="flex shrink-0 justify-end pt-4">
          <Button variant="outline" onClick={onClose}>
            닫기
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
