'use client';

import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';

interface props {
  onClose: () => void;
}

export function AddPrevProblemsDialog({ onClose }: props) {

  return (
    <Dialog open={true} onOpenChange={onClose}>
      <DialogContent className="flex max-h-[90vh] max-w-2xl flex-col">
        <DialogHeader>
          <DialogTitle>가입 이전에 풀었던 문제 등록하기</DialogTitle>
          <DialogDescription>가입 이전에 풀었던 문제들을 자동으로 등록 가능합니다.</DialogDescription>
        </DialogHeader>


        <div className="flex shrink-0 justify-end gap-2 pt-4">
          <Button variant="outline" onClick={onClose}>
            닫기
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
