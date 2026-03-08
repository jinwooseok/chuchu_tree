'use client';

import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from '@/components/ui/alert-dialog';

interface StudyLeaveAlertDialogProps {
  studyName: string;
  isPending: boolean;
  onConfirm: () => void;
  onClose: () => void;
}

export function StudyLeaveAlertDialog({ studyName, isPending, onConfirm, onClose }: StudyLeaveAlertDialogProps) {
  return (
    <AlertDialog open={true} onOpenChange={(open) => !open && onClose()}>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>스터디에서 탈퇴하시겠습니까?</AlertDialogTitle>
          <AlertDialogDescription>
            {`"`}
            {studyName}
            {`"`} 스터디에서 탈퇴합니다. 탈퇴 후에는 다시 가입 신청이 필요합니다.
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel disabled={isPending}>취소</AlertDialogCancel>
          <AlertDialogAction onClick={onConfirm} disabled={isPending}>
            {isPending ? '처리 중...' : '탈퇴하기'}
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}
