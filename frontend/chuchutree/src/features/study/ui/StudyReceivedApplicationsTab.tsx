'use client';

import { Loader2 } from 'lucide-react';
import { StudyDetail, useStudyApplications, useAcceptApplication, useRejectApplication } from '@/entities/study';
import { toast } from '@/lib/utils/toast';
import { UserAvatar } from '@/components/custom/UserAvatar';

const STATUS_LABEL: Record<string, string> = {
  PENDING: '대기중',
  ACCEPTED: '수락됨',
  REJECTED: '거절됨',
};

const STATUS_CLASS: Record<string, string> = {
  PENDING: 'bg-yellow-100 text-yellow-800',
  ACCEPTED: 'bg-green-100 text-green-800',
  REJECTED: 'bg-red-100 text-red-800',
};

interface StudyReceivedApplicationsTabProps {
  studyDetail: StudyDetail;
  isOwner: boolean;
}

export function StudyReceivedApplicationsTab({ studyDetail, isOwner }: StudyReceivedApplicationsTabProps) {
  const { data: applications = [], isLoading } = useStudyApplications(studyDetail.studyId);

  const { mutate: acceptApplication, isPending: isAccepting } = useAcceptApplication(studyDetail.studyId, {
    onError: () => toast.error('신청 수락에 실패했습니다.'),
  });

  const { mutate: rejectApplication, isPending: isRejecting } = useRejectApplication(studyDetail.studyId, {
    onError: () => toast.error('신청 거절에 실패했습니다.'),
  });

  const isActing = isAccepting || isRejecting;

  if (!isOwner) {
    // 비방장: pendingApplications만 표시
    return (
      <div className="space-y-2">
        {studyDetail.pendingApplications.length === 0 ? (
          <p className="text-muted-foreground py-4 text-center text-sm">받은 신청이 없습니다.</p>
        ) : (
          studyDetail.pendingApplications.map((app) => (
            <div key={app.applicationId} className="flex items-center justify-between rounded-lg border p-3">
              <div className="flex items-center gap-2">
                <UserAvatar profileImageUrl={app.profileImageUrl} bjAccountId={app.applicantBjAccountId} userCode={app.applicantUserCode} size={24} />
                <span className="text-sm">
                  {app.applicantBjAccountId}#{app.applicantUserCode}
                </span>
              </div>
              <span className="text-muted-foreground text-xs">{app.createdAt.slice(0, 10)}</span>
            </div>
          ))
        )}
      </div>
    );
  }

  // 방장: 전체 신청 목록 + 수락/거절 기능
  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-6">
        <Loader2 className="text-muted-foreground h-5 w-5 animate-spin" />
      </div>
    );
  }

  if (applications.length === 0) {
    return <p className="text-muted-foreground py-4 text-center text-sm">받은 신청이 없습니다.</p>;
  }

  return (
    <div className="space-y-2">
      {applications.map((app) => (
        <div key={app.applicationId} className="flex items-center justify-between rounded-lg border p-3">
          <div className="flex items-center gap-2">
            <UserAvatar profileImageUrl={app.applicantProfileImageUrl} bjAccountId={app.applicantBjAccountId} userCode={app.applicantUserCode} size={24} />
            <span className="text-sm font-medium">
              {app.applicantBjAccountId}#{app.applicantUserCode}
            </span>
            <span className={`rounded px-1.5 py-0.5 text-xs font-medium ${STATUS_CLASS[app.status] ?? ''}`}>
              {STATUS_LABEL[app.status] ?? app.status}
            </span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-muted-foreground text-xs">{app.createdAt.slice(0, 10)}</span>
            {app.status === 'PENDING' && (
              <>
                <button
                  onClick={() => acceptApplication(app.applicationId)}
                  disabled={isActing}
                  className="text-xs font-medium text-green-600 transition-colors hover:text-green-700"
                >
                  수락
                </button>
                <button
                  onClick={() => rejectApplication(app.applicationId)}
                  disabled={isActing}
                  className="text-destructive hover:text-destructive/80 text-xs font-medium transition-colors"
                >
                  거절
                </button>
              </>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
