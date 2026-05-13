'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Loader2 } from 'lucide-react';
import { StudyDetail, useUpdateStudy } from '@/entities/study';
import { toast } from '@/lib/utils/toast';

interface StudyEditFormProps {
  studyDetail: StudyDetail;
  onClose: () => void;
}

export function StudyEditForm({ studyDetail, onClose }: StudyEditFormProps) {
  const [description, setDescription] = useState(studyDetail.description);
  const [maxMembers, setMaxMembers] = useState(studyDetail.maxMembers);

  const { mutate: updateStudy, isPending } = useUpdateStudy(studyDetail.studyId, {
    onSuccess: () => {
      toast.success('스터디 정보가 수정되었습니다.');
      onClose();
    },
    onError: () => {
      toast.error('스터디 정보 수정에 실패했습니다.');
    },
  });

  const handleSubmit = () => {
    updateStudy({ description: description.trim(), maxMembers });
  };

  return (
    <div className="space-y-3">
      <div className="flex flex-col gap-1.5">
        <label className="text-muted-foreground text-xs">설명</label>
        <Textarea
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="스터디 설명을 입력하세요"
          className="resize-none"
          rows={3}
        />
      </div>

      <div className="flex flex-col gap-1.5">
        <label className="text-muted-foreground text-xs">최대 인원 (최대 10명)</label>
        <Input
          type="number"
          min={studyDetail.memberCount}
          max={10}
          value={maxMembers}
          onChange={(e) => setMaxMembers(Math.max(studyDetail.memberCount, Math.min(10, Number(e.target.value))))}
          className="w-24"
        />
      </div>

      <div className="flex justify-end gap-2">
        <Button variant="outline" size="sm" onClick={onClose} disabled={isPending}>
          취소
        </Button>
        <Button size="sm" onClick={handleSubmit} disabled={isPending}>
          {isPending && <Loader2 className="mr-1.5 h-3.5 w-3.5 animate-spin" />}
          저장
        </Button>
      </div>
    </div>
  );
}
