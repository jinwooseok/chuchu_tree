'use client';

import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { useNotificationStore } from '@/lib/store/notification';
import { useState, useEffect } from 'react';
import { Bell, CalendarPlus, CheckCheck, ClipboardList, Megaphone, TrendingUp, UserCheck, UserPlus, Users } from 'lucide-react';
import { WillSolveProblems, SolvedProblems } from '@/entities/calendar/model/calendar.types';
import { TIER_INFO, TierNumKey } from '@/shared/constants/tierSystem';

// ─── Types ────────────────────────────────────────────────────────────────────

export type NoticeCategory = 'study-invitation-status' | 'study-application-status' | 'study-problems-status' | 'user-problems-status' | 'user-tier-status' | 'system-announcement' | 'study-received-invitation' | 'study-received-application';

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
  studyName: string;
  problem: WillSolveProblems;
  calendarDate: string; // YYYY-MM-DD
}

export interface UserProblemsNotice extends BaseNotice {
  category: 'user-problems-status';
  problem: SolvedProblems;
  date: string; // YYYY-MM-DD
}

export interface UserTierNotice extends BaseNotice {
  category: 'user-tier-status';
  tierLevel: TierNumKey;
}

export interface SystemAnnouncementNotice extends BaseNotice {
  category: 'system-announcement';
  text: string;
}

export interface StudyReceivedInvitationNotice extends BaseNotice {
  category: 'study-received-invitation';
  studyName: string;
  inviterUserId: string; // bjAccountId
  inviterUserCode: string; // defaultCode
  status: NoticeStatusValue;
}

export interface StudyReceivedApplicationNotice extends BaseNotice {
  category: 'study-received-application';
  studyName: string;
  applicantUserId: string; // bjAccountId
  applicantUserCode: string; // defaultCode
  status: NoticeStatusValue;
}

export type Notice = StudyInvitationNotice | StudyApplicationNotice | StudyProblemsNotice | UserProblemsNotice | UserTierNotice | SystemAnnouncementNotice | StudyReceivedInvitationNotice | StudyReceivedApplicationNotice;

// ─── Tab ─────────────────────────────────────────────────────────────────────

type NoticeTab = 'study' | 'personal' | 'announcement';

const STUDY_CATEGORIES: NoticeCategory[] = ['study-received-invitation', 'study-received-application', 'study-invitation-status', 'study-application-status', 'study-problems-status'];
const PERSONAL_CATEGORIES: NoticeCategory[] = ['user-problems-status', 'user-tier-status'];
const ANNOUNCEMENT_CATEGORIES: NoticeCategory[] = ['system-announcement'];

// ─── Mock Data (SSE 연동 전 임시 데이터) ─────────────────────────────────────

const MOCK_NOTICES: Notice[] = [
  {
    id: 10,
    category: 'study-received-application',
    isRead: false,
    createdAt: new Date(Date.now() - 1000 * 60 * 8).toISOString(),
    studyName: 'mock스터디05',
    applicantUserId: 'user04',
    applicantUserCode: '1111',
    status: 'pending',
  },
  {
    id: 9,
    category: 'study-received-invitation',
    isRead: false,
    createdAt: new Date(Date.now() - 1000 * 60 * 5).toISOString(),
    studyName: 'mock스터디05',
    inviterUserId: 'user03',
    inviterUserCode: '9999',
    status: 'pending',
  },
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
  {
    id: 5,
    category: 'study-problems-status',
    isRead: false,
    createdAt: new Date(Date.now() - 1000 * 60 * 10).toISOString(),
    studyName: 'mock스터디01',
    problem: {
      problemId: 2557,
      problemTitle: '선분 교차 1',
      problemTierLevel: 14,
      problemTierName: 'G2',
      problemClassLevel: null,
      tags: [],
      representativeTag: null,
    },
    calendarDate: '2026-02-28',
  },
  {
    id: 6,
    category: 'user-problems-status',
    isRead: false,
    createdAt: new Date(Date.now() - 1000 * 60 * 15).toISOString(),
    problem: {
      problemId: 1000,
      problemTitle: '수 정렬하기',
      problemTierLevel: 6,
      problemTierName: 'S5',
      problemClassLevel: 1,
      realSolvedYn: true,
      tags: [],
      representativeTag: null,
    },
    date: '2026-02-25',
  },
  {
    id: 7,
    category: 'user-tier-status',
    isRead: true,
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 5).toISOString(),
    tierLevel: 11,
  },
  {
    id: 8,
    category: 'system-announcement',
    isRead: false,
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString(),
    text: '2026년 3월 업데이트 안내: 스터디 기능이 추가되었습니다. 친구들과 함께 문제를 풀어보세요!',
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

function formatCalendarDate(dateString: string): string {
  const [, month, day] = dateString.split('-');
  return `${parseInt(month)}월 ${parseInt(day)}일`;
}

const STATUS_CONFIG: Record<NoticeStatusValue, { label: string; className: string }> = {
  pending: { label: '대기 중', className: 'text-muted-foreground' },
  accepted: { label: '수락됨', className: 'text-advanced-bg' },
  rejected: { label: '거절됨', className: 'text-excluded-bg' },
};

const CATEGORY_LABEL: Record<NoticeCategory, string> = {
  'study-received-invitation': '스터디 초대 받음',
  'study-received-application': '가입 신청 받음',
  'study-invitation-status': '스터디 초대',
  'study-application-status': '가입 신청',
  'study-problems-status': '문제 등록',
  'user-problems-status': '문제 업데이트',
  'user-tier-status': '티어 상승',
  'system-announcement': '공지사항',
};

const CATEGORY_ICON: Record<NoticeCategory, React.ReactNode> = {
  'study-received-invitation': <UserPlus className="mt-0.5 h-4 w-4 shrink-0" />,
  'study-received-application': <UserCheck className="mt-0.5 h-4 w-4 shrink-0" />,
  'study-invitation-status': <Users className="mt-0.5 h-4 w-4 shrink-0" />,
  'study-application-status': <ClipboardList className="mt-0.5 h-4 w-4 shrink-0" />,
  'study-problems-status': <CalendarPlus className="mt-0.5 h-4 w-4 shrink-0" />,
  'user-problems-status': <CheckCheck className="mt-0.5 h-4 w-4 shrink-0" />,
  'user-tier-status': <TrendingUp className="mt-0.5 h-4 w-4 shrink-0" />,
  'system-announcement': <Megaphone className="mt-0.5 h-4 w-4 shrink-0" />,
};

// ─── Notice Card ──────────────────────────────────────────────────────────────

interface NoticeCardProps {
  notice: Notice;
  showUnreadDot: boolean;
  onCancel: (id: number) => void;
  onAccept?: (id: number) => void;
  onReject?: (id: number) => void;
  onApprove?: (id: number) => void;
  onDecline?: (id: number) => void;
}

function NoticeCard({ notice, showUnreadDot, onCancel, onAccept, onReject, onApprove, onDecline }: NoticeCardProps) {
  const renderBody = () => {
    switch (notice.category) {
      case 'study-received-application': {
        const n = notice as StudyReceivedApplicationNotice;
        return (
          <p className="text-sm leading-snug">
            <span className="font-medium">
              {n.applicantUserId}#{n.applicantUserCode}
            </span>
            님이 <span className="font-medium">{n.studyName}</span> 스터디에 가입 신청했습니다.
          </p>
        );
      }
      case 'study-received-invitation': {
        const n = notice as StudyReceivedInvitationNotice;
        return (
          <p className="text-sm leading-snug">
            <span className="font-medium">
              {n.inviterUserId}#{n.inviterUserCode}
            </span>
            님이 <span className="font-medium">{n.studyName}</span> 스터디에 초대했습니다.
          </p>
        );
      }
      case 'study-invitation-status': {
        const n = notice as StudyInvitationNotice;
        return (
          <p className="text-sm leading-snug">
            <span className="font-medium">{n.studyName}</span> 스터디에
            <span className="font-medium">
              {n.userId}#{n.userCode}
            </span>
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
      case 'study-problems-status': {
        const n = notice as StudyProblemsNotice;
        return (
          <p className="text-sm leading-snug">
            <span className="font-medium">{n.studyName}</span> 스터디에{' '}
            <span className="font-medium">
              #{n.problem.problemId} {n.problem.problemTitle}
            </span>{' '}
            문제가 {formatCalendarDate(n.calendarDate)}에 등록되었습니다.
          </p>
        );
      }
      case 'user-problems-status': {
        const n = notice as UserProblemsNotice;
        return (
          <p className="text-sm leading-snug">
            {formatCalendarDate(n.date)}에
            <span className="text-primary bg-logo mx-1 rounded-xs px-1 font-medium">
              #{n.problem.problemId} {n.problem.problemTitle}
            </span>
            문제가 등록되었습니다.
          </p>
        );
      }
      case 'user-tier-status': {
        const n = notice as UserTierNotice;
        return (
          <p className="text-sm leading-snug">
            티어가{' '}
            <span className="text-primary bg-logo mx-1 rounded-xs px-1 font-medium">
              {TIER_INFO[n.tierLevel].name} {TIER_INFO[n.tierLevel].num}
            </span>
            로 상승했습니다!
          </p>
        );
      }
      case 'system-announcement': {
        const n = notice as SystemAnnouncementNotice;
        return <p className="text-sm leading-snug">{n.text}</p>;
      }
    }
  };

  const renderStatus = () => {
    if (
      notice.category !== 'study-invitation-status' &&
      notice.category !== 'study-application-status' &&
      notice.category !== 'study-received-invitation' &&
      notice.category !== 'study-received-application'
    ) return null;
    const n = notice as StudyInvitationNotice | StudyApplicationNotice | StudyReceivedInvitationNotice | StudyReceivedApplicationNotice;
    if (n.status === 'pending') return null;
    const { label, className } = STATUS_CONFIG[n.status];
    return <span className={`text-xs font-medium ${className}`}>{label}</span>;
  };

  const canCancel =
    (notice.category === 'study-invitation-status' || notice.category === 'study-application-status') && (notice as StudyInvitationNotice | StudyApplicationNotice).status === 'pending';

  const canRespond =
    notice.category === 'study-received-invitation' && (notice as StudyReceivedInvitationNotice).status === 'pending';

  const canApprove =
    notice.category === 'study-received-application' && (notice as StudyReceivedApplicationNotice).status === 'pending';

  return (
    <div className="bg-innerground-hovergray/50 hover:bg-innerground-darkgray/70 relative flex items-start gap-3 rounded-lg p-3 transition-colors">
      {showUnreadDot && <div className="bg-primary absolute -top-0.5 -right-0.5 h-2 w-2 rounded-full" />}

      <span className="text-muted-foreground">{CATEGORY_ICON[notice.category]}</span>

      <div className="flex flex-1 flex-col gap-1.5">
        <div className="flex items-center gap-4">
          <span className="text-muted-foreground text-xs font-semibold tracking-wide uppercase">{CATEGORY_LABEL[notice.category]}</span>
          <span className="text-muted-foreground text-xs">{formatRelativeTime(notice.createdAt)}</span>
        </div>

        {renderBody()}

        <div className="flex items-center justify-start gap-2">
          <div className="flex items-center gap-2">{renderStatus()}</div>

          {canCancel && (
            <Button variant="ghost" size="sm" className="hover:bg-destructive/10 hover:text-destructive text-muted-foreground h-7 px-2 text-xs" onClick={() => onCancel(notice.id)}>
              {CATEGORY_LABEL[notice.category]} 취소하기
            </Button>
          )}

          {canRespond && (
            <>
              <Button variant="ghost" size="sm" className="hover:bg-advanced-bg/10 text-advanced-bg h-7 px-2 text-xs" onClick={() => onAccept?.(notice.id)}>
                가입하기
              </Button>
              <Button variant="ghost" size="sm" className="hover:bg-destructive/10 hover:text-destructive text-muted-foreground h-7 px-2 text-xs" onClick={() => onReject?.(notice.id)}>
                거절하기
              </Button>
            </>
          )}

          {canApprove && (
            <>
              <Button variant="ghost" size="sm" className="hover:bg-advanced-bg/10 text-advanced-bg h-7 px-2 text-xs" onClick={() => onApprove?.(notice.id)}>
                승인하기
              </Button>
              <Button variant="ghost" size="sm" className="hover:bg-destructive/10 hover:text-destructive text-muted-foreground h-7 px-2 text-xs" onClick={() => onDecline?.(notice.id)}>
                거절하기
              </Button>
            </>
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
  const [activeTab, setActiveTab] = useState<NoticeTab>('study');

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

  const handleAccept = (id: number) => {
    setNotices((prev) => prev.map((n) => (n.id === id ? { ...n, status: 'accepted' } as Notice : n)));
    // TODO: acceptStudyInvitation(id) API 연동 예정
  };

  const handleReject = (id: number) => {
    setNotices((prev) => prev.map((n) => (n.id === id ? { ...n, status: 'rejected' } as Notice : n)));
    // TODO: rejectStudyInvitation(id) API 연동 예정
  };

  const handleApprove = (id: number) => {
    setNotices((prev) => prev.map((n) => (n.id === id ? { ...n, status: 'accepted' } as Notice : n)));
    // TODO: approveStudyApplication(id) API 연동 예정
  };

  const handleDecline = (id: number) => {
    setNotices((prev) => prev.map((n) => (n.id === id ? { ...n, status: 'rejected' } as Notice : n)));
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
                <NoticeCard key={notice.id} notice={notice} showUnreadDot={initiallyUnreadIds.has(notice.id)} onCancel={handleCancel} onAccept={handleAccept} onReject={handleReject} onApprove={handleApprove} onDecline={handleDecline} />
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
