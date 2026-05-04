'use client';

import { Button } from '@/components/ui/button';
import { TIER_INFO } from '@/shared/constants/tierSystem';
import {
  BaseNotice,
  isRequestedStudyInvitation,
  isResponsedStudyInvitation,
  isRequestedStudyApplication,
  isResponsedStudyApplication,
  isAssignedStudyProblem,
  isUpdatedUserProblem,
  isUpdatedUserTier,
  isSystemAnnouncement,
} from '@/entities/notice';
import { UserAvatar } from '@/components/custom/UserAvatar';
import { CATEGORY_DETAIL_LABEL, CATEGORY_ICON, STATUS_CONFIG } from '../model/notice.config';
import { formatCalendarDate, formatRelativeTime } from '../lib/utils';

export interface NoticeCardProps {
  notice: BaseNotice;
  showUnreadDot: boolean;
  onGoToDetail: (notice: BaseNotice) => void;
}

export function NoticeCard({ notice, showUnreadDot, onGoToDetail }: NoticeCardProps) {
  const renderAvatar = () => {
    if (isRequestedStudyInvitation(notice)) {
      const c = notice.content;
      return <UserAvatar profileImageUrl={c.profileImageUrl} bjAccountId={c.inviterBjAccountId} userCode={c.inviterUserCode} size={28} />;
    }
    if (isResponsedStudyInvitation(notice)) {
      const c = notice.content;
      return <UserAvatar profileImageUrl={c.profileImageUrl} bjAccountId={c.inviteeBjAccountId} userCode={c.inviteeUserCode} size={28} />;
    }
    if (isRequestedStudyApplication(notice)) {
      const c = notice.content;
      return <UserAvatar profileImageUrl={c.profileImageUrl} bjAccountId={c.applicantBjAccountId} userCode={c.applicantUserCode} size={28} />;
    }
    if (isResponsedStudyApplication(notice)) {
      const c = notice.content;
      return <UserAvatar profileImageUrl={c.profileImageUrl} bjAccountId={c.ownerBjAccountId} userCode={c.ownerUserCode} size={28} />;
    }
    if (isAssignedStudyProblem(notice)) {
      const c = notice.content;
      return <UserAvatar profileImageUrl={c.profileImageUrl} bjAccountId={c.assignerBjAccountId} userCode={c.assignerUserCode} size={28} />;
    }
    return null;
  };

  const renderBody = () => {
    // 티어 상승 알림: 티어 이미지/배지 강조
    if (isUpdatedUserTier(notice)) {
      const c = notice.content;
      return (
        <p className="text-sm leading-snug">
          티어가{' '}
          <span className="text-primary bg-logo mx-1 rounded-xs px-1 font-medium">
            {TIER_INFO[c.tierLevel].name} {TIER_INFO[c.tierLevel].num}
          </span>
          로 상승했습니다!
        </p>
      );
    }

    // 문제 업데이트 알림: 문제 목록 표시
    if (isUpdatedUserProblem(notice)) {
      const c = notice.content;
      const firstEntry = c.problemsByDate[0];
      if (!firstEntry) return <p className="text-sm leading-snug">{notice.message}</p>;
      const firstProblem = firstEntry.problems[0];
      const totalCount = c.problemsByDate.reduce((sum, e) => sum + e.problems.length, 0);
      return (
        <p className="text-sm leading-snug">
          {formatCalendarDate(firstEntry.solvedDate)}에{' '}
          {firstProblem && (
            <span className="text-primary bg-logo mx-1 rounded-xs px-1 font-medium">
              #{firstProblem.problemId} {firstProblem.problemTitle}
            </span>
          )}
          {totalCount > 1 ? ` 외 ${totalCount - 1}개 문제가` : '문제가'} 등록되었습니다.
        </p>
      );
    }

    // 스터디 문제 등록 알림
    if (isAssignedStudyProblem(notice)) {
      const c = notice.content;
      return (
        <p className="text-sm leading-snug">
          <span className="font-medium">{c.studyName}</span> 스터디에{' '}
          <span className="font-medium">
            #{c.problemId} {c.problemTitle}
          </span>{' '}
          문제가 {formatCalendarDate(c.calendarDate)}에 등록되었습니다.
        </p>
      );
    }

    // 그 외는 서버에서 내려오는 message 필드 사용
    return <p className="text-sm leading-snug">{notice.message}</p>;
  };

  const renderStatus = () => {
    if (isResponsedStudyInvitation(notice) || isResponsedStudyApplication(notice)) {
      const status = notice.content.status;
      if (status === 'PENDING') return null;
      const { label, className } = STATUS_CONFIG[status];
      return <span className={`text-xs font-medium ${className}`}>{label}</span>;
    }
    return null;
  };

  const canGoToDetail = notice.categoryDetail === 'REQUESTED_STUDY_INVITATION' || notice.categoryDetail === 'REQUESTED_STUDY_APPLICATION';

  const avatar = renderAvatar();

  return (
    <div className="bg-innerground-hovergray/50 hover:bg-innerground-darkgray/70 relative flex items-start gap-3 rounded-lg p-3 transition-colors">
      {showUnreadDot && <div className="bg-primary absolute -top-0.5 -right-0.5 h-2 w-2 rounded-full" />}

      {/* 아이콘 or 아바타 */}
      {avatar ? (
        <div className="mt-0.5 shrink-0">{avatar}</div>
      ) : (
        <span className="text-muted-foreground">{CATEGORY_ICON[notice.category]}</span>
      )}

      <div className="flex flex-1 flex-col gap-1.5">
        <div className="flex items-center gap-4">
          <span className="text-muted-foreground text-xs font-semibold tracking-wide uppercase">{CATEGORY_DETAIL_LABEL[notice.categoryDetail]}</span>
          <span className="text-muted-foreground text-xs">{formatRelativeTime(notice.createdAt)}</span>
        </div>

        {renderBody()}

        {(renderStatus() || canGoToDetail) && (
          <div className="flex items-center gap-2">
            {renderStatus()}
            {canGoToDetail && (
              <Button variant="ghost" size="sm" className="text-primary hover:bg-primary/10 h-7 px-2 text-xs" onClick={() => onGoToDetail(notice)}>
                확인하러가기
              </Button>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
