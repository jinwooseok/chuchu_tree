'use client';

import { useState } from 'react';
import { StudyDetail, useLeaveStudy, useDeleteStudy } from '@/entities/study';
import { useLayoutStore } from '@/lib/store/layout';
import { toast } from '@/lib/utils/toast';
import { StudyEditForm } from './StudyEditForm';
import { StudyLeaveAlertDialog } from './StudyLeaveAlertDialog';
import { StudyDeleteAlertDialog } from './StudyDeleteAlertDialog';
import { StudyKickMemberDialog } from './StudyKickMemberDialog';

type SettingView = 'menu' | 'edit' | 'kick';

interface StudySettingsPanelProps {
  studyDetail: StudyDetail;
  currentUserAccountId: number;
  isOwner: boolean;
}

export function StudySettingsPanel({ studyDetail, currentUserAccountId, isOwner }: StudySettingsPanelProps) {
  const [view, setView] = useState<SettingView>('menu');
  const [isLeaveOpen, setIsLeaveOpen] = useState(false);
  const [isDeleteOpen, setIsDeleteOpen] = useState(false);

  const setCenterSection = useLayoutStore((s) => s.setCenterSection);

  const { mutate: leaveStudy, isPending: isLeaving } = useLeaveStudy({
    onSuccess: () => {
      toast.success('스터디에서 탈퇴했습니다.');
      setCenterSection('calendar');
    },
    onError: () => toast.error('스터디 탈퇴에 실패했습니다.'),
  });

  const { mutate: deleteStudy, isPending: isDeleting } = useDeleteStudy({
    onSuccess: () => {
      toast.success('스터디가 삭제되었습니다.');
      setCenterSection('calendar');
    },
    onError: () => toast.error('스터디 삭제에 실패했습니다.'),
  });

  return (
    <div className="mt-3 rounded-lg border p-4">
      <p className="mb-3 text-sm font-medium">설정</p>

      {view === 'menu' && (
        <div className="space-y-1">
          {isOwner && (
            <button
              onClick={() => setView('edit')}
              className="hover:bg-muted w-full rounded px-3 py-2 text-left text-sm transition-colors"
            >
              스터디 정보 수정
            </button>
          )}
          <button
            onClick={() => setIsLeaveOpen(true)}
            className="text-destructive hover:bg-destructive/10 w-full rounded px-3 py-2 text-left text-sm transition-colors"
          >
            스터디 탈퇴
          </button>
          {isOwner && (
            <>
              <button
                onClick={() => setView('kick')}
                className="hover:bg-muted w-full rounded px-3 py-2 text-left text-sm transition-colors"
              >
                멤버 강제 퇴장
              </button>
              <button
                onClick={() => setIsDeleteOpen(true)}
                className="text-destructive hover:bg-destructive/10 w-full rounded px-3 py-2 text-left text-sm transition-colors"
              >
                스터디 삭제
              </button>
            </>
          )}
        </div>
      )}

      {view === 'edit' && (
        <StudyEditForm studyDetail={studyDetail} onClose={() => setView('menu')} />
      )}

      {view === 'kick' && (
        <StudyKickMemberDialog
          studyDetail={studyDetail}
          currentUserAccountId={currentUserAccountId}
          onClose={() => setView('menu')}
        />
      )}

      {isLeaveOpen && (
        <StudyLeaveAlertDialog
          studyName={studyDetail.studyName}
          isPending={isLeaving}
          onConfirm={() => leaveStudy(studyDetail.studyId)}
          onClose={() => setIsLeaveOpen(false)}
        />
      )}

      {isDeleteOpen && (
        <StudyDeleteAlertDialog
          studyName={studyDetail.studyName}
          isPending={isDeleting}
          onConfirm={() => deleteStudy(studyDetail.studyId)}
          onClose={() => setIsDeleteOpen(false)}
        />
      )}
    </div>
  );
}
