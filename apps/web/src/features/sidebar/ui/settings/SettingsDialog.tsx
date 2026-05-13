'use client';

import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Separator } from '@/components/ui/separator';
import { TargetCode } from '@/shared/constants/tagSystem';

import ThemeSection from './ThemeSection';
import BjAccountSection from './BjAccountSection';
import TargetSection from './TargetSection';
import PolicyLinksSection from './PolicyLinksSection';
import AccountDeletionSection from './AccountDeletionSection';
import UserProfileSection from '@/features/sidebar/ui/settings/UserProfileSection';

interface SettingsDialogProps {
  onClose: () => void;
  currentBjAccountId: string;
  currentTarget: TargetCode;
  linkedAt?: string;
  currentUserCode: string;
  currentProfileImageUrl: string | null;
  isLanding?: boolean;
}

export function SettingsDialog({ onClose, currentBjAccountId, currentTarget, linkedAt, currentUserCode, currentProfileImageUrl, isLanding = false }: SettingsDialogProps) {
  return (
    <Dialog open={true} onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="flex max-h-[90vh] flex-col sm:max-w-2xl">
        <DialogHeader>
          <DialogTitle>설정</DialogTitle>
          <DialogDescription>계정 및 애플리케이션 설정을 관리합니다.</DialogDescription>
        </DialogHeader>

        <div className="flex-1 space-y-6 overflow-y-auto py-4 pr-4">
          <ThemeSection />

          <Separator />
          {!isLanding && <UserProfileSection currentBjAccountId={currentBjAccountId} currentUserCode={currentUserCode} currentProfileImageUrl={currentProfileImageUrl} />}

          <BjAccountSection currentBjAccountId={currentBjAccountId} linkedAt={linkedAt} onClose={onClose} isLanding={isLanding} />

          <Separator />

          <TargetSection currentTarget={currentTarget} onClose={onClose} isLanding={isLanding} />

          <Separator />

          <PolicyLinksSection />

          <Separator className="border-destructive/20 mb-20" />

          <AccountDeletionSection isLanding={isLanding} />
        </div>
      </DialogContent>
    </Dialog>
  );
}
