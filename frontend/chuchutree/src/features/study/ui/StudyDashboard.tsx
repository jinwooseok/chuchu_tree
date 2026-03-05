'use client';

import { useState } from 'react';
import { StudyDetail } from '@/entities/study';
import { StudyHeader } from './StudyHeader';
import { StudySettingsPanel } from './StudySettingsPanel';
import { StudyInviteDialog } from './StudyInviteDialog';

interface StudyDashboardProps {
  studyDetail: StudyDetail;
  currentUserAccountId: number;
}

export function StudyDashboard({ studyDetail, currentUserAccountId }: StudyDashboardProps) {
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [isInviteOpen, setIsInviteOpen] = useState(false);

  const isOwner = studyDetail.ownerUserAccountId === currentUserAccountId;

  return (
    <div className="hide-scrollbar flex h-full w-full overflow-y-auto">
      <div className="w-full max-w-2xl space-y-4 p-2">
        <StudyHeader
          studyDetail={studyDetail}
          currentUserAccountId={currentUserAccountId}
          onSettingsClick={() => setIsSettingsOpen((prev) => !prev)}
          onInviteClick={() => setIsInviteOpen(true)}
        />

        {isSettingsOpen && (
          <StudySettingsPanel
            studyDetail={studyDetail}
            currentUserAccountId={currentUserAccountId}
            isOwner={isOwner}
          />
        )}

        {isInviteOpen && (
          <StudyInviteDialog
            studyDetail={studyDetail}
            isOwner={isOwner}
            onClose={() => setIsInviteOpen(false)}
          />
        )}
      </div>
    </div>
  );
}
