'use client';

import { useState } from 'react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { usePatchBjAccount } from '@/entities/bj-account';
import { toast } from '@/lib/utils/toast';

interface BjAccountSectionProps {
  currentBjAccountId: string;
  linkedAt?: string;
  onClose: () => void;
}

const canChangeAccount = (linkedAt?: string) => {
  if (!linkedAt) return false;
  const linkedDate = new Date(linkedAt);
  const now = new Date();
  const diffInDays = Math.floor((now.getTime() - linkedDate.getTime()) / (1000 * 60 * 60 * 24));
  return diffInDays >= 7;
};

const getAvailableDate = (linkedAt?: string) => {
  if (!linkedAt) return '';
  const linkedDate = new Date(linkedAt);
  const availableDate = new Date(linkedDate);
  availableDate.setDate(availableDate.getDate() + 7);
  const dateString = availableDate.toLocaleDateString().split('.').slice(1);
  return `${dateString[0]}월${dateString[1]}일`;
};

export default function BjAccountSection({ currentBjAccountId, linkedAt, onClose }: BjAccountSectionProps) {
  const [newBjAccountId, setNewBjAccountId] = useState('');
  const canChange = canChangeAccount(linkedAt);
  const availableDateString = getAvailableDate(linkedAt);

  const { mutate: patchAccount, isPending } = usePatchBjAccount({
    onSuccess: () => {
      toast.success('백준 계정이 변경되었습니다.');
      setNewBjAccountId('');
      onClose();
    },
    onError: () => {
      toast.error('계정 변경에 실패했습니다. 다시 시도해주세요.');
    },
  });

  const handleSubmit = () => {
    if (!newBjAccountId.trim()) {
      toast.error('새로운 백준 아이디를 입력해주세요.');
      return;
    }
    patchAccount({ bjAccount: newBjAccountId.trim() });
  };

  return (
    <div className="space-y-3">
      <div>
        <h3 className="text-sm font-semibold">백준 계정 변경</h3>
        <p className="text-muted-foreground text-xs">연동된 백준 계정을 재설정합니다. (7일에 한 번만 가능)</p>
      </div>

      <div className="space-y-3 rounded-lg border p-4">
        <div className="space-y-2">
          <label className="text-xs font-medium">현재 백준 아이디</label>
          <Input value={currentBjAccountId} disabled />
        </div>

        <div className="space-y-2">
          <label className="text-xs font-medium">새 백준 아이디</label>
          <Input value={newBjAccountId} onChange={(e) => setNewBjAccountId(e.target.value)} placeholder="새로운 백준 아이디를 입력하세요" disabled={!canChange || isPending} />
          {!canChange && <p className="text-destructive text-xs">계정 재설정은 {availableDateString} 이후에 가능합니다.</p>}
        </div>

        <div className="flex justify-end">
          <Button onClick={handleSubmit} disabled={!canChange || isPending || !newBjAccountId.trim()}>
            {isPending ? '변경 중...' : '저장'}
          </Button>
        </div>
      </div>
    </div>
  );
}
