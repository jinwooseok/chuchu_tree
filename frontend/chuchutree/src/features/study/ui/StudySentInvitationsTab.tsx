'use client';

import { useState, useEffect } from 'react';
import { Loader2, Search } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { StudyDetail, useStudyInvitations, useSendInvitation, useCancelInvitation, useSearchUsers, SearchedUser } from '@/entities/study';
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

interface StudySentInvitationsTabProps {
  studyDetail: StudyDetail;
  isOwner: boolean;
}

export function StudySentInvitationsTab({ studyDetail, isOwner }: StudySentInvitationsTabProps) {
  const [isInviting, setIsInviting] = useState(false);
  const [userSearchKeyword, setUserSearchKeyword] = useState('');
  const [debouncedKeyword, setDebouncedKeyword] = useState('');

  useEffect(() => {
    const timer = setTimeout(() => setDebouncedKeyword(userSearchKeyword), 400);
    return () => clearTimeout(timer);
  }, [userSearchKeyword]);

  const { data: invitations = [], isLoading: isLoadingInvitations } = useStudyInvitations(studyDetail.studyId);
  const { data: userSearchResults = [], isLoading: isSearchingUsers } = useSearchUsers(debouncedKeyword);

  const { mutate: sendInvitation, isPending: isSending } = useSendInvitation(studyDetail.studyId, {
    onSuccess: () => {
      toast.success('초대를 발송했습니다.');
      setUserSearchKeyword('');
      setIsInviting(false);
    },
    onError: () => toast.error('초대 발송에 실패했습니다.'),
  });

  const { mutate: cancelInvitation, isPending: isCanceling } = useCancelInvitation(studyDetail.studyId, {
    onError: () => toast.error('초대 취소에 실패했습니다.'),
  });

  const handleSelectUser = (user: SearchedUser) => {
    sendInvitation(user.userAccountId);
  };

  if (!isOwner) {
    // 비방장: pendingInvitations만 표시
    return (
      <div className="space-y-2">
        {studyDetail.pendingInvitations.length === 0 ? (
          <p className="text-muted-foreground py-4 text-center text-sm">보낸 초대가 없습니다.</p>
        ) : (
          studyDetail.pendingInvitations.map((inv) => (
            <div key={inv.invitationId} className="flex items-center justify-between rounded-lg border p-3">
              <div className="flex items-center gap-2">
                <UserAvatar profileImageUrl={inv.profileImageUrl} bjAccountId={inv.inviteeBjAccountId} userCode={inv.inviteeUserCode} size={24} />
                <span className="text-sm">
                  {inv.inviteeBjAccountId}#{inv.inviteeUserCode}
                </span>
              </div>
              <span className="text-muted-foreground text-xs">{inv.createdAt.slice(0, 10)}</span>
            </div>
          ))
        )}
      </div>
    );
  }

  // 방장: 전체 초대 목록 + 초대하기 기능
  return (
    <div className="space-y-3">
      <div className="flex justify-end">
        <Button size="sm" variant="outline" onClick={() => setIsInviting((prev) => !prev)}>
          초대하기
        </Button>
      </div>

      {isInviting && (
        <div className="space-y-2">
          <div className="relative">
            <Search className="text-muted-foreground absolute top-1/2 left-3 h-4 w-4 -translate-y-1/2" />
            <Input
              value={userSearchKeyword}
              onChange={(e) => setUserSearchKeyword(e.target.value)}
              placeholder="백준 아이디 또는 코드로 검색"
              className="pl-9"
              autoFocus
            />
          </div>

          {debouncedKeyword && (
            <div className="bg-background overflow-hidden rounded-lg border">
              {isSearchingUsers ? (
                <div className="flex items-center justify-center py-4">
                  <Loader2 className="text-muted-foreground h-4 w-4 animate-spin" />
                </div>
              ) : userSearchResults.length > 0 ? (
                userSearchResults.map((u) => (
                  <button
                    key={u.userAccountId}
                    className="hover:bg-muted flex w-full items-center justify-between px-3 py-2 text-sm transition-colors"
                    onClick={() => handleSelectUser(u)}
                    disabled={isSending}
                  >
                    <div className="flex items-center gap-2">
                      <UserAvatar profileImageUrl={u.profileImageUrl} bjAccountId={u.bjAccountId} userCode={u.userCode} size={24} />
                      <span className="font-medium">{u.bjAccountId}</span>
                    </div>
                    <span className="text-muted-foreground">#{u.userCode}</span>
                  </button>
                ))
              ) : (
                <p className="text-muted-foreground py-4 text-center text-sm">검색 결과가 없습니다.</p>
              )}
            </div>
          )}
        </div>
      )}

      {isLoadingInvitations ? (
        <div className="flex items-center justify-center py-6">
          <Loader2 className="text-muted-foreground h-5 w-5 animate-spin" />
        </div>
      ) : invitations.length === 0 ? (
        <p className="text-muted-foreground py-4 text-center text-sm">보낸 초대가 없습니다.</p>
      ) : (
        <div className="space-y-2">
          {invitations.map((inv) => (
            <div key={inv.invitationId} className="flex items-center justify-between rounded-lg border p-3">
              <div className="flex items-center gap-2">
                <UserAvatar profileImageUrl={inv.inviterProfileImageUrl} bjAccountId={inv.inviterBjAccountId} userCode={inv.inviterUserCode} size={24} />
                <span className="text-sm font-medium">
                  {inv.inviterBjAccountId}#{inv.inviterUserCode}
                </span>
                <span className={`rounded px-1.5 py-0.5 text-xs font-medium ${STATUS_CLASS[inv.status] ?? ''}`}>
                  {STATUS_LABEL[inv.status] ?? inv.status}
                </span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-muted-foreground text-xs">{inv.createdAt.slice(0, 10)}</span>
                {inv.status === 'PENDING' && (
                  <button
                    onClick={() => cancelInvitation(inv.invitationId)}
                    disabled={isCanceling}
                    className="text-destructive hover:text-destructive/80 text-xs font-medium transition-colors"
                  >
                    취소
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
