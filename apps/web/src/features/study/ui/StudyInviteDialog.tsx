'use client';

import { useState } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog';
import { StudyDetail } from '@/entities/study';
import { StudySentInvitationsTab } from './StudySentInvitationsTab';
import { StudyReceivedApplicationsTab } from './StudyReceivedApplicationsTab';

type TabType = 'sent' | 'received';

interface StudyInviteDialogProps {
  studyDetail: StudyDetail;
  isOwner: boolean;
  onClose: () => void;
  defaultTab?: TabType;
}

export function StudyInviteDialog({ studyDetail, isOwner, onClose, defaultTab = 'sent' }: StudyInviteDialogProps) {
  const [activeTab, setActiveTab] = useState<TabType>(defaultTab);

  return (
    <Dialog open={true} onOpenChange={onClose}>
      <DialogContent className="flex max-h-[80vh] max-w-lg flex-col">
        <DialogHeader>
          <DialogTitle>초대 관리</DialogTitle>
          <DialogDescription>{studyDetail.studyName}</DialogDescription>
        </DialogHeader>

        {/* 탭 전환 */}
        <div className="flex border-b">
          <button
            className={`flex-1 py-2 text-sm font-medium transition-colors ${activeTab === 'sent' ? 'border-primary text-foreground border-b-2' : 'text-muted-foreground hover:text-foreground'}`}
            onClick={() => setActiveTab('sent')}
          >
            보낸 초대
          </button>
          <button
            className={`flex-1 py-2 text-sm font-medium transition-colors ${activeTab === 'received' ? 'border-primary text-foreground border-b-2' : 'text-muted-foreground hover:text-foreground'}`}
            onClick={() => setActiveTab('received')}
          >
            받은 신청
          </button>
        </div>

        <div className="min-h-0 flex-1 overflow-y-auto pr-1">
          {activeTab === 'sent' ? (
            <StudySentInvitationsTab studyDetail={studyDetail} isOwner={isOwner} />
          ) : (
            <StudyReceivedApplicationsTab studyDetail={studyDetail} isOwner={isOwner} />
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}
