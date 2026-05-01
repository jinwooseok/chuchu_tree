'use client';

import { useState, useEffect } from 'react';
import { StudyDetail, useUpdateStudy } from '@/entities/study';
import { toast } from '@/lib/utils/toast';
import { StudyHeader } from './StudyHeader';
import { StudySettingsPanel } from './StudySettingsPanel';
import { StudyInviteDialog } from './StudyInviteDialog';
import { useNotificationStore } from '@/lib/store/notification';

export type SettingsView = 'menu' | 'edit' | 'kick';

interface StudyDashboardProps {
  studyDetail: StudyDetail;
  currentUserAccountId: number;
}

export function StudyDashboard({ studyDetail, currentUserAccountId }: StudyDashboardProps) {
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [isInviteOpen, setIsInviteOpen] = useState(false);
  const [inviteDefaultTab, setInviteDefaultTab] = useState<'sent' | 'received'>('sent');
  const [settingsView, setSettingsView] = useState<SettingsView>('menu');

  const { pendingStudyInviteAction, setPendingStudyInviteAction } = useNotificationStore();

  // 알림에서 "확인하러가기" 클릭 시 자동으로 received 탭 열기
  useEffect(() => {
    if (pendingStudyInviteAction && pendingStudyInviteAction.studyId === studyDetail.studyId) {
      setInviteDefaultTab(pendingStudyInviteAction.tab);
      setIsInviteOpen(true);
      setPendingStudyInviteAction(null);
    }
  }, [pendingStudyInviteAction, studyDetail.studyId, setPendingStudyInviteAction]);

  // 인라인 수정 상태
  const [editDescription, setEditDescription] = useState('');
  const [editMaxMembers, setEditMaxMembers] = useState(0);

  const isOwner = studyDetail.ownerUserAccountId === currentUserAccountId;
  const isEditing = settingsView === 'edit';

  const { mutate: updateStudy, isPending: isSaving } = useUpdateStudy(studyDetail.studyId, {
    onSuccess: () => {
      toast.success('스터디 정보가 수정되었습니다.');
      setSettingsView('menu');
    },
    onError: () => toast.error('스터디 정보 수정에 실패했습니다.'),
  });

  const handleSettingsClick = () => {
    setIsSettingsOpen((prev) => {
      if (prev) setSettingsView('menu'); // 닫힐 때 메뉴로 리셋
      return !prev;
    });
  };

  const handleStartEdit = () => {
    setEditDescription(studyDetail.description);
    setEditMaxMembers(studyDetail.maxMembers);
    setSettingsView('edit');
  };

  const handleCancelEdit = () => setSettingsView('menu');

  const handleSaveEdit = () => {
    updateStudy({ description: editDescription.trim(), maxMembers: editMaxMembers });
  };

  return (
    <div className="flex w-full flex-col">
      {/* 상단영역 */}
      <div className="flex w-full flex-col gap-2 lg:flex-row">
        <div className="min-w-0 flex-1">
          <StudyHeader
            studyDetail={studyDetail}
            currentUserAccountId={currentUserAccountId}
            onSettingsClick={handleSettingsClick}
            onInviteClick={() => setIsInviteOpen(true)}
            isEditing={isEditing}
            editDescription={editDescription}
            editMaxMembers={editMaxMembers}
            onEditDescriptionChange={setEditDescription}
            onEditMaxMembersChange={setEditMaxMembers}
          />
        </div>

        {isSettingsOpen && (
          <div className="w-full lg:w-60 lg:shrink-0">
            <StudySettingsPanel
              studyDetail={studyDetail}
              currentUserAccountId={currentUserAccountId}
              isOwner={isOwner}
              settingsView={settingsView}
              setSettingsView={setSettingsView}
              onStartEdit={handleStartEdit}
              onCancelEdit={handleCancelEdit}
              onSaveEdit={handleSaveEdit}
              isSaving={isSaving}
            />
          </div>
        )}
      </div>
      {/* 모달 */}
      {isInviteOpen && <StudyInviteDialog studyDetail={studyDetail} isOwner={isOwner} defaultTab={inviteDefaultTab} onClose={() => { setIsInviteOpen(false); setInviteDefaultTab('sent'); }} />}
    </div>
  );
}
