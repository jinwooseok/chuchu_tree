'use client';

import { useState } from 'react';
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from '@/components/ui/alert-dialog';
import { StudyDetail, StudyMember, useKickMember } from '@/entities/study';
import { toast } from '@/lib/utils/toast';
import { UserAvatar } from '@/components/custom/UserAvatar';

interface StudyKickMemberDialogProps {
  studyDetail: StudyDetail;
  currentUserAccountId: number;
  onClose: () => void;
}

export function StudyKickMemberDialog({ studyDetail, currentUserAccountId, onClose }: StudyKickMemberDialogProps) {
  const [selectedMember, setSelectedMember] = useState<StudyMember | null>(null);

  const kickableMembers = studyDetail.members.filter((m) => m.userAccountId !== currentUserAccountId);

  const { mutate: kickMember, isPending } = useKickMember(studyDetail.studyId, {
    onSuccess: () => {
      toast.success('강제 퇴장 완료');
      setSelectedMember(null);
      onClose();
    },
    onError: () => {
      toast.error('멤버 강제 퇴장에 실패했습니다.');
    },
  });

  return (
    <>
      {kickableMembers.length === 0 ? (
        <p className="text-muted-foreground text-sm">퇴장할 수 있는 멤버가 없습니다.</p>
      ) : (
        <div className="divide-y">
          {kickableMembers.map((member) => (
            <div key={member.userAccountId} className="flex items-center justify-between py-2">
              <div className="flex items-center gap-2">
                <UserAvatar profileImageUrl={member.profileImageUrl} bjAccountId={member.bjAccountId} userCode={member.userCode} size={24} />
                <span className="truncate text-sm">
                  {member.bjAccountId}#{member.userCode}
                </span>
              </div>
              <button onClick={() => setSelectedMember(member)} className="text-destructive hover:text-destructive/80 text-xs font-medium whitespace-nowrap transition-colors">
                퇴장
              </button>
            </div>
          ))}
        </div>
      )}

      {selectedMember && (
        <AlertDialog open={true} onOpenChange={(open) => !open && setSelectedMember(null)}>
          <AlertDialogContent>
            <AlertDialogHeader>
              <AlertDialogTitle>멤버를 강제 퇴장하시겠습니까?</AlertDialogTitle>
              <AlertDialogDescription>
                {selectedMember.bjAccountId}#{selectedMember.userCode} 님을 스터디에서 퇴장시킵니다.
              </AlertDialogDescription>
            </AlertDialogHeader>
            <AlertDialogFooter>
              <AlertDialogCancel disabled={isPending}>취소</AlertDialogCancel>
              <AlertDialogAction onClick={() => kickMember(selectedMember.userAccountId)} disabled={isPending}>
                {isPending ? '처리 중...' : '퇴장시키기'}
              </AlertDialogAction>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialog>
      )}
    </>
  );
}
