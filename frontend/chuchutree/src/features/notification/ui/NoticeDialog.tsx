'use client';

import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { useNotificationStore } from '@/lib/store/notification';
import { useState, useEffect } from 'react';
import { Bell } from 'lucide-react';
import { Notice, NoticeTab } from '../model/notice.types';
import { ANNOUNCEMENT_CATEGORIES, MOCK_NOTICES, PERSONAL_CATEGORIES, STUDY_CATEGORIES } from '../model/notice.constants';
import { NoticeCard } from './NoticeCard';

interface Props {
  onClose: () => void;
}

export function NoticeDialog({ onClose }: Props) {
  const { setHasUnread } = useNotificationStore();
  const [activeTab, setActiveTab] = useState<NoticeTab>('study');

  // 최신순 정렬 (SSE 연동 시 SSE 데이터로 교체 예정)
  const [notices, setNotices] = useState<Notice[]>(() => [...MOCK_NOTICES].sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()));

  // 모달 열었을 당시 읽지 않은 알림 ID 스냅샷 — dot 표시 기준
  const [initiallyUnreadIds] = useState<Set<number>>(() => new Set(MOCK_NOTICES.filter((n) => !n.isRead).map((n) => n.id)));

  // 모달 오픈 시 bell dot 제거 + 전체 읽음 API 요청
  // dot 표시는 initiallyUnreadIds 스냅샷 기준이므로 충돌 없음
  useEffect(() => {
    setHasUnread(false);
    // TODO: markAllNoticesAsRead() API 연동 예정
  }, [setHasUnread]);

  const handleCancel = (id: number) => {
    setNotices((prev) => prev.filter((n) => n.id !== id));
    // TODO: cancelNotice(id) API 연동 예정
  };

  const handleAccept = (id: number) => {
    setNotices((prev) => prev.map((n) => (n.id === id ? ({ ...n, status: 'accepted' } as Notice) : n)));
    // TODO: acceptStudyInvitation(id) API 연동 예정
  };

  const handleReject = (id: number) => {
    setNotices((prev) => prev.map((n) => (n.id === id ? ({ ...n, status: 'rejected' } as Notice) : n)));
    // TODO: rejectStudyInvitation(id) API 연동 예정
  };

  const handleApprove = (id: number) => {
    setNotices((prev) => prev.map((n) => (n.id === id ? ({ ...n, status: 'accepted' } as Notice) : n)));
    // TODO: approveStudyApplication(id) API 연동 예정
  };

  const handleDecline = (id: number) => {
    setNotices((prev) => prev.map((n) => (n.id === id ? ({ ...n, status: 'rejected' } as Notice) : n)));
    // TODO: declineStudyApplication(id) API 연동 예정
  };

  const tabCategories = activeTab === 'study' ? STUDY_CATEGORIES : activeTab === 'personal' ? PERSONAL_CATEGORIES : ANNOUNCEMENT_CATEGORIES;
  const filteredNotices = notices.filter((n) => tabCategories.includes(n.category));

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
          <button
            className={`flex-1 py-2 text-sm font-medium transition-colors ${activeTab === 'study' ? 'border-primary text-foreground border-b-2' : 'text-muted-foreground hover:text-foreground'}`}
            onClick={() => setActiveTab('study')}
          >
            스터디 알림
          </button>
          <button
            className={`flex-1 py-2 text-sm font-medium transition-colors ${activeTab === 'personal' ? 'border-primary text-foreground border-b-2' : 'text-muted-foreground hover:text-foreground'}`}
            onClick={() => setActiveTab('personal')}
          >
            내 알림
          </button>
          <button
            className={`flex-1 py-2 text-sm font-medium transition-colors ${activeTab === 'announcement' ? 'border-primary text-foreground border-b-2' : 'text-muted-foreground hover:text-foreground'}`}
            onClick={() => setActiveTab('announcement')}
          >
            공지사항
          </button>
        </div>

        {filteredNotices.length > 0 ? (
          <div className="min-h-0 flex-1 overflow-y-auto pt-2 pr-1">
            <div className="space-y-2">
              {filteredNotices.map((notice) => (
                <NoticeCard
                  key={notice.id}
                  notice={notice}
                  showUnreadDot={initiallyUnreadIds.has(notice.id)}
                  onCancel={handleCancel}
                  onAccept={handleAccept}
                  onReject={handleReject}
                  onApprove={handleApprove}
                  onDecline={handleDecline}
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
