'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { usePostTarget } from '@/entities/user';
import { TARGET_OPTIONS } from '@/shared/constants/target';
import { TargetCode } from '@/shared/constants/tagSystem';
import { toast } from '@/lib/utils/toast';

interface TargetSectionProps {
  currentTarget: TargetCode;
  onClose: () => void;
}

export default function TargetSection({ currentTarget, onClose }: TargetSectionProps) {
  const [selectedTarget, setSelectedTarget] = useState<TargetCode>(currentTarget);

  // currentTarget이 변경되면 selectedTarget 초기화
  useEffect(() => {
    setSelectedTarget(currentTarget);
  }, [currentTarget]);

  const { mutate: postTarget, isPending } = usePostTarget({
    onSuccess: () => {
      toast.success('목표가 변경되었습니다.');
      onClose();
    },
    onError: () => {
      toast.error('목표 변경에 실패했습니다. 다시 시도해주세요.');
    },
  });

  const handleTargetChange = () => {
    postTarget({ targetCode: selectedTarget });
  };

  return (
    <div className="space-y-3">
      <div>
        <h3 className="text-sm font-semibold">학습 목표</h3>
        <p className="text-muted-foreground text-xs">학습 목표에 따라 추천 문제가 달라집니다.</p>
      </div>

      <div className="space-y-2 rounded-lg border p-4">
        {TARGET_OPTIONS.map((option) => (
          <label
            key={option.code}
            className={`flex cursor-pointer items-start gap-3 rounded-lg border-2 p-3 transition-all ${
              selectedTarget === option.code ? 'border-primary bg-primary/5' : 'border-input hover:border-primary/50'
            } ${isPending ? 'cursor-not-allowed opacity-50' : ''}`}
          >
            <input
              type="radio"
              name="target"
              value={option.code}
              checked={selectedTarget === option.code}
              onChange={(e) => setSelectedTarget(e.target.value as TargetCode)}
              disabled={isPending}
              className="text-primary focus:ring-primary mt-1 h-4 w-4"
            />
            <div className="flex-1">
              <div className="mb-1 flex items-center gap-2">
                <div className="text-sm font-medium">{option.label}</div>
                <div className="text-muted-foreground text-xs">{option.description}</div>
              </div>
              <div className="text-muted-foreground text-xs">{option.description2}</div>
            </div>
          </label>
        ))}

        <div className="flex justify-end pt-2">
          <Button onClick={handleTargetChange} disabled={isPending || selectedTarget === currentTarget}>
            {isPending ? '변경 중...' : '저장'}
          </Button>
        </div>
      </div>
    </div>
  );
}
