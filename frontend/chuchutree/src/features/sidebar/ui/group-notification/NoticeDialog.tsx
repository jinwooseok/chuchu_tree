'use client';

import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { useNotificationStore } from '@/lib/store/notification';
import { useState, useEffect } from 'react';
import { Bell, BookOpen, ClipboardList, Users } from 'lucide-react';

// ─── Types ────────────────────────────────────────────────────────────────────

export type NoticeCategory = 'study-invitation-status' | 'study-application-status' | 'study-problems-status' | 'user-problems-status';
// 추후 카테고리 추가 예정

export type NoticeStatusValue = 'pending' | 'accepted' | 'rejected';

interface BaseNotice {
  id: number;
  category: NoticeCategory;
  isRead: boolean;
  createdAt: string; // ISO 8601
}

export interface StudyInvitationNotice extends BaseNotice {
  category: 'study-invitation-status';
  studyName: string;
  userId: string; // bjAccountId
  userCode: string; // defaultCode
  status: NoticeStatusValue;
}

export interface StudyApplicationNotice extends BaseNotice {
  category: 'study-application-status';
  studyName: string;
  status: NoticeStatusValue;
}

export interface StudyProblemsNotice extends BaseNotice {
  category: 'study-problems-status';
  // TBD
}

export interface UserProblemsNotice extends BaseNotice {
  category: 'user-problems-status';
  // TBD
}

export type Notice = StudyInvitationNotice | StudyApplicationNotice | StudyProblemsNotice | UserProblemsNotice;

// ─── Mock Data (SSE 연동 전 임시 데이터) ─────────────────────────────────────

const MOCK_NOTICES: Notice[] = [
  {
    id: 1,
    category: 'study-invitation-status',
    isRead: false,
    createdAt: new Date(Date.now() - 1000 * 60 * 3).toISOString(),
    studyName: 'mock스터디01',
    userId: 'user01',
    userCode: '1234',
    status: 'pending',
  },
  {
    id: 2,
    category: 'study-application-status',
    isRead: false,
    createdAt: new Date(Date.now() - 1000 * 60 * 28).toISOString(),
    studyName: 'mock스터디02',
    status: 'accepted',
  },
  {
    id: 3,
    category: 'study-invitation-status',
    isRead: true,
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 3).toISOString(),
    studyName: 'mock스터디03',
    userId: 'user02',
    userCode: '5678',
    status: 'rejected',
  },
  {
    id: 4,
    category: 'study-application-status',
    isRead: true,
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 26).toISOString(),
    studyName: 'mock스터디04',
    status: 'pending',
  },
];

// ─── Helpers ──────────────────────────────────────────────────────────────────

function formatRelativeTime(isoString: string): string {
  const diff = Date.now() - new Date(isoString).getTime();
  const minutes = Math.floor(diff / 60000);
  if (minutes < 1) return '방금 전';
  if (minutes < 60) return `${minutes}분 전`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}시간 전`;
  const days = Math.floor(hours / 24);
  return `${days}일 전`;
}

const STATUS_CONFIG: Record<NoticeStatusValue, { label: string; className: string }> = {
  pending: { label: '대기 중', className: 'text-muted-foreground' },
  accepted: { label: '수락됨', className: 'text-advanced-bg' },
  rejected: { label: '거절됨', className: 'text-excluded-bg' },
};

const CATEGORY_LABEL: Record<NoticeCategory, string> = {
  'study-invitation-status': '스터디 초대',
  'study-application-status': '가입 신청',
  'study-problems-status': '스터디 문제',
  'user-problems-status': '개인 문제',
};

const CATEGORY_ICON: Record<NoticeCategory, React.ReactNode> = {
  'study-invitation-status': <Users className="mt-0.5 h-4 w-4 shrink-0" />,
  'study-application-status': <ClipboardList className="mt-0.5 h-4 w-4 shrink-0" />,
  'study-problems-status': <BookOpen className="mt-0.5 h-4 w-4 shrink-0" />,
  'user-problems-status': <BookOpen className="mt-0.5 h-4 w-4 shrink-0" />,
};

// ─── Notice Card ──────────────────────────────────────────────────────────────

interface NoticeCardProps {
  notice: Notice;
  showUnreadDot: boolean;
  onCancel: (id: number) => void;
}

function NoticeCard({ notice, showUnreadDot, onCancel }: NoticeCardProps) {
  const renderBody = () => {
    switch (notice.category) {
      case 'study-invitation-status': {
        const n = notice as StudyInvitationNotice;
        return (
          <p className="text-sm leading-snug">
            <span className="font-medium">{n.studyName}</span> 스터디에{' '}
            <span className="font-medium">
              {n.userId}#{n.userCode}
            </span>{' '}
            님을 초대했습니다.
          </p>
        );
      }
      case 'study-application-status': {
        const n = notice as StudyApplicationNotice;
        const suffix = n.status === 'accepted' ? '이 수락되었습니다.' : n.status === 'rejected' ? '이 거절되었습니다.' : '중입니다.';
        return (
          <p className="text-sm leading-snug">
            <span className="font-medium">{n.studyName}</span> 스터디 가입 신청{suffix}
          </p>
        );
      }
      case 'study-problems-status':
      case 'user-problems-status':
        return <p className="text-muted-foreground text-sm">알림 내용이 준비 중입니다.</p>;
    }
  };

  const renderStatus = () => {
    if (notice.category !== 'study-invitation-status' && notice.category !== 'study-application-status') return null;
    const n = notice as StudyInvitationNotice | StudyApplicationNotice;
    const { label, className } = STATUS_CONFIG[n.status];
    return <span className={`text-xs font-medium ${className}`}>{label}</span>;
  };

  const canCancel =
    (notice.category === 'study-invitation-status' || notice.category === 'study-application-status') && (notice as StudyInvitationNotice | StudyApplicationNotice).status === 'pending';

  return (
    <div className="bg-innerground-hovergray/50 hover:bg-innerground-darkgray/70 relative flex items-start gap-3 rounded-lg p-3 transition-colors">
      {showUnreadDot && <div className="bg-primary absolute -top-0.5 -right-0.5 h-2 w-2 rounded-full" />}

      <span className="text-muted-foreground">{CATEGORY_ICON[notice.category]}</span>

      <div className="flex flex-1 flex-col gap-1.5">
        <div className="flex items-center gap-1.5">
          <span className="text-muted-foreground text-xs font-semibold tracking-wide uppercase">{CATEGORY_LABEL[notice.category]}</span>
        </div>

        {renderBody()}

        <div className="flex items-center justify-start gap-2">
          <div className="flex items-center gap-2">
            {renderStatus()}
            <span className="text-muted-foreground text-xs">{formatRelativeTime(notice.createdAt)}</span>
          </div>

          {canCancel && (
            <Button variant="ghost" size="sm" className="hover:bg-destructive/10 hover:text-destructive text-muted-foreground h-7 px-2 text-xs" onClick={() => onCancel(notice.id)}>
              {CATEGORY_LABEL[notice.category]} 취소하기
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}

// ─── Main Component ───────────────────────────────────────────────────────────

interface props {
  onClose: () => void;
}

export function NoticeDialog({ onClose }: props) {
  const { setHasUnread } = useNotificationStore();

  // 최신순 정렬 (SSE 연동 시 SSE 데이터로 교체 예정)
  const [notices, setNotices] = useState<Notice[]>(() => [...MOCK_NOTICES].sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()));

  // 모달 열었을 당시 읽지 않은 알림 ID 스냅샷 — dot 표시 기준 (요구사항 8)
  const [initiallyUnreadIds] = useState<Set<number>>(() => new Set(MOCK_NOTICES.filter((n) => !n.isRead).map((n) => n.id)));

  // 모달 오픈 시 bell dot 제거 + 전체 읽음 API 요청 (요구사항 9)
  // dot 표시는 initiallyUnreadIds 스냅샷 기준이므로 충돌 없음
  useEffect(() => {
    setHasUnread(false);
    // TODO: markAllNoticesAsRead() API 연동 예정
  }, [setHasUnread]);

  const handleCancel = (id: number) => {
    setNotices((prev) => prev.filter((n) => n.id !== id));
    // TODO: cancelNotice(id) API 연동 예정
  };

  return (
    <Dialog open={true} onOpenChange={onClose}>
      <DialogContent className="flex max-h-[90vh] max-w-xl flex-col">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Bell className="h-4 w-4" />
            알림
          </DialogTitle>
        </DialogHeader>
        {notices.length > 0 ? (
          <div className="min-h-0 flex-1 overflow-y-auto pt-2 pr-1">
            <div className="space-y-2">
              {notices.map((notice) => (
                <NoticeCard key={notice.id} notice={notice} showUnreadDot={initiallyUnreadIds.has(notice.id)} onCancel={handleCancel} />
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
