'use client';

import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';

interface TagBanAlertDialogProps {
  tagDisplayName: string;
  recommendationYn: boolean;
  isPending: boolean;
  onConfirm: () => void;
  onClose: () => void;
}

export function TagBanAlertDialog({ tagDisplayName, recommendationYn, isPending, onConfirm, onClose }: TagBanAlertDialogProps) {
  return (
    <AlertDialog open={true} onOpenChange={(open) => !open && onClose()}>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>{recommendationYn ? '추천 목록에서 제외하시겠습니까?' : '추천 목록에 추가하시겠습니까?'}</AlertDialogTitle>
          <AlertDialogDescription>
            {recommendationYn ? `"${tagDisplayName}" 유형을 추천 목록에서 제외합니다. 제외된 유형은 문제 추천 시 포함되지 않습니다.` : `"${tagDisplayName}" 유형을 추천 목록에 추가합니다. 이 유형의 문제가 추천될 수 있습니다.`}
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel disabled={isPending}>취소</AlertDialogCancel>
          <AlertDialogAction onClick={onConfirm} disabled={isPending}>
            {isPending ? '처리 중...' : recommendationYn ? '제외하기' : '추가하기'}
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}
