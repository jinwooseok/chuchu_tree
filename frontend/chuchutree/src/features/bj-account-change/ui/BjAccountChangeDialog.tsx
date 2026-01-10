'use client';

import { useState } from 'react';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { usePatchBjAccount } from '@/entities/bj-account';
import { toast } from 'sonner';

interface BjAccountChangeDialogProps {
  currentBjAccountId: string;
  onClose: () => void;
}

export function BjAccountChangeDialog({ currentBjAccountId, onClose }: BjAccountChangeDialogProps) {
  const [newBjAccountId, setNewBjAccountId] = useState('');

  const { mutate: patchAccount, isPending } = usePatchBjAccount({
    onSuccess: () => {
      toast.success('백준 계정이 변경되었습니다.', { position: 'top-center' });
      onClose();
    },
    onError: () => {
      toast.error('계정 변경에 실패했습니다. 다시 시도해주세요.', { position: 'top-center' });
    },
  });

  const handleSubmit = () => {
    if (!newBjAccountId.trim()) {
      toast.error('백준 아이디를 입력해주세요.', { position: 'top-center' });
      return;
    }
    patchAccount({ bjAccount: newBjAccountId.trim() });
  };

  return (
    <Dialog open={true} onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>연동 계정 재설정</DialogTitle>
          <DialogDescription>백준 계정을 변경하시겠습니까? 재설정은 7일에 한 번만 가능합니다.</DialogDescription>
        </DialogHeader>
        <div className="space-y-4 py-4">
          <div className="space-y-2">
            <label className="text-sm font-medium">현재 백준 아이디</label>
            <input type="text" value={currentBjAccountId} disabled className="bg-muted text-muted-foreground w-full rounded-md border px-3 py-2 text-sm" />
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium">새 백준 아이디</label>
            <input
              type="text"
              value={newBjAccountId}
              onChange={(e) => setNewBjAccountId(e.target.value)}
              placeholder="새로운 백준 아이디를 입력하세요"
              disabled={isPending}
              className="focus:ring-primary w-full rounded-md border px-3 py-2 text-sm focus:ring-2 focus:outline-none disabled:cursor-not-allowed disabled:opacity-50"
            />
          </div>
        </div>
        <DialogFooter className="sm:justify-end">
          <button
            type="button"
            onClick={onClose}
            disabled={isPending}
            className="border-input bg-background hover:bg-accent hover:text-accent-foreground rounded-md border px-4 py-2 text-sm font-medium transition-colors disabled:cursor-not-allowed disabled:opacity-50"
          >
            취소
          </button>
          <button
            type="button"
            onClick={handleSubmit}
            disabled={isPending}
            className="bg-primary text-primary-foreground hover:bg-primary/90 rounded-md px-4 py-2 text-sm font-medium transition-colors disabled:cursor-not-allowed disabled:opacity-50"
          >
            {isPending ? '변경 중...' : '변경하기'}
          </button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
