'use client';

import { Button } from '@/components/ui/button';
import { TIER_INFO } from '@/shared/constants/tierSystem';
import {
  Notice,
  StudyApplicationNotice,
  StudyInvitationNotice,
  StudyProblemsNotice,
  StudyReceivedApplicationNotice,
  StudyReceivedInvitationNotice,
  SystemAnnouncementNotice,
  UserProblemsNotice,
  UserTierNotice,
} from '../model/notice.types';
import { CATEGORY_ICON, CATEGORY_LABEL, STATUS_CONFIG } from '../model/notice.config';
import { formatCalendarDate, formatRelativeTime } from '../lib/utils';

export interface NoticeCardProps {
  notice: Notice;
  showUnreadDot: boolean;
  onCancel: (id: number) => void;
  onAccept?: (id: number) => void;
  onReject?: (id: number) => void;
  onApprove?: (id: number) => void;
  onDecline?: (id: number) => void;
}

export function NoticeCard({ notice, showUnreadDot, onCancel, onAccept, onReject, onApprove, onDecline }: NoticeCardProps) {
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
    )
      return null;
    const n = notice as StudyInvitationNotice | StudyApplicationNotice | StudyReceivedInvitationNotice | StudyReceivedApplicationNotice;
    if (n.status === 'pending') return null;
    const { label, className } = STATUS_CONFIG[n.status];
    return <span className={`text-xs font-medium ${className}`}>{label}</span>;
  };

  const canCancel =
    (notice.category === 'study-invitation-status' || notice.category === 'study-application-status') &&
    (notice as StudyInvitationNotice | StudyApplicationNotice).status === 'pending';

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
