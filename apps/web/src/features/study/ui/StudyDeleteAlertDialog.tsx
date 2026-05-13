'use client';

import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from '@/components/ui/alert-dialog';

interface StudyDeleteAlertDialogProps {
  studyName: string;
  isPending: boolean;
  onConfirm: () => void;
  onClose: () => void;
}

export function StudyDeleteAlertDialog({ studyName, isPending, onConfirm, onClose }: StudyDeleteAlertDialogProps) {
  return (
    <AlertDialog open={true} onOpenChange={(open) => !open && onClose()}>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>스터디를 삭제하시겠습니까?</AlertDialogTitle>
          <AlertDialogDescription>
            "{studyName}" 스터디를 삭제합니다. 이 작업은 되돌릴 수 없습니다.
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel disabled={isPending}>취소</AlertDialogCancel>
          <AlertDialogAction onClick={onConfirm} disabled={isPending}>
            {isPending ? '처리 중...' : '삭제하기'}
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}
