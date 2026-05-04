'use client';

import { Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { StudyDetail, useLeaveStudy, useDeleteStudy } from '@/entities/study';
import { useLayoutStore } from '@/lib/store/layout';
import { toast } from '@/lib/utils/toast';
import { StudyLeaveAlertDialog } from './StudyLeaveAlertDialog';
import { StudyDeleteAlertDialog } from './StudyDeleteAlertDialog';
import { StudyKickMemberDialog } from './StudyKickMemberDialog';
import { useState } from 'react';
import type { SettingsView } from './StudyDashboard';

interface StudySettingsPanelProps {
  studyDetail: StudyDetail;
  currentUserAccountId: number;
  isOwner: boolean;
  settingsView: SettingsView;
  setSettingsView: (view: SettingsView) => void;
  onStartEdit: () => void;
  onCancelEdit: () => void;
  onSaveEdit: () => void;
  isSaving: boolean;
}

const VIEW_TITLE: Record<SettingsView, string> = {
  menu: '설정',
  edit: '스터디 정보수정',
  kick: '멤버강제퇴장',
};

export function StudySettingsPanel({ studyDetail, currentUserAccountId, isOwner, settingsView, setSettingsView, onStartEdit, onCancelEdit, onSaveEdit, isSaving }: StudySettingsPanelProps) {
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
    <div className="flex w-full flex-col rounded-lg border p-4 sm:h-full">
      {/* 패널 헤더: 동적 제목 + 뷰별 액션 버튼 */}
      <div className="mb-3 flex shrink-0 items-center justify-between">
        <p className="text-sm font-medium">{VIEW_TITLE[settingsView]}</p>

        {settingsView === 'edit' && (
          <div className="flex gap-1.5">
            <Button variant="outline" size="sm" onClick={onCancelEdit} disabled={isSaving} className="h-7 px-2 text-xs">
              취소
            </Button>
            <Button size="sm" onClick={onSaveEdit} disabled={isSaving} className="h-7 px-2 text-xs">
              {isSaving && <Loader2 className="mr-1 h-3 w-3 animate-spin" />}
              저장
            </Button>
          </div>
        )}

        {settingsView === 'kick' && (
          <button onClick={() => setSettingsView('menu')} className="text-muted-foreground hover:text-foreground text-xs transition-colors">
            취소
          </button>
        )}
      </div>

      {/* 콘텐츠 */}
      <div className="hide-scrollbar min-h-0 flex-1 overflow-y-auto">
        {settingsView === 'menu' && (
          <div className="space-y-1">
            {isOwner && (
              <button onClick={onStartEdit} className="hover:bg-muted w-full rounded px-3 py-2 text-left text-sm whitespace-nowrap transition-colors">
                스터디 정보 수정
              </button>
            )}
            <button onClick={() => setIsLeaveOpen(true)} className="text-destructive hover:bg-destructive/10 w-full rounded px-3 py-2 text-left text-sm whitespace-nowrap transition-colors">
              스터디 탈퇴
            </button>
            {isOwner && (
              <>
                <button onClick={() => setSettingsView('kick')} className="hover:bg-muted w-full rounded px-3 py-2 text-left text-sm whitespace-nowrap transition-colors">
                  멤버 강제 퇴장
                </button>
                <button onClick={() => setIsDeleteOpen(true)} className="text-destructive hover:bg-destructive/10 w-full rounded px-3 py-2 text-left text-sm whitespace-nowrap transition-colors">
                  스터디 삭제
                </button>
              </>
            )}
          </div>
        )}

        {settingsView === 'kick' && (
          <StudyKickMemberDialog
            studyDetail={studyDetail}
            currentUserAccountId={currentUserAccountId}
            onClose={() => setSettingsView('menu')}
          />
        )}
      </div>

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
