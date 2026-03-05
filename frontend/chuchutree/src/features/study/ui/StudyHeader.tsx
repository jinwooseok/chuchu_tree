'use client';

import { Settings, UserPlus } from 'lucide-react';
import { StudyDetail, StudyMember } from '@/entities/study';

interface StudyHeaderProps {
  studyDetail: StudyDetail;
  currentUserAccountId: number;
  onSettingsClick: () => void;
  onInviteClick: () => void;
}

function MemberRow({ member }: { member: StudyMember }) {
  const isOwner = member.role === 'OWNER';
  return (
    <div className="flex items-center justify-between py-1.5">
      <div className="flex items-center gap-2">
        <span className="text-sm font-medium">
          {member.bjAccountId}#{member.userCode}
        </span>
        {isOwner && (
          <span className="bg-primary/10 text-primary rounded px-1.5 py-0.5 text-xs font-medium">
            방장
          </span>
        )}
      </div>
      <span className="text-muted-foreground text-xs">
        가입일: {member.joinedAt.slice(0, 10)}
      </span>
    </div>
  );
}

export function StudyHeader({ studyDetail, currentUserAccountId, onSettingsClick, onInviteClick }: StudyHeaderProps) {
  const ownerMember = studyDetail.members.find((m) => m.userAccountId === studyDetail.ownerUserAccountId);
  const ownerLabel = ownerMember ? `${ownerMember.bjAccountId}#${ownerMember.userCode}` : String(studyDetail.ownerUserAccountId);

  return (
    <div className="rounded-lg border p-4">
      {/* 헤더 행: 스터디명 + 아이콘 */}
      <div className="mb-2 flex items-center justify-between">
        <h2 className="text-lg font-bold">{studyDetail.studyName}</h2>
        <div className="flex items-center gap-1">
          <button
            onClick={onSettingsClick}
            className="text-muted-foreground hover:text-foreground rounded p-1 transition-colors"
            aria-label="스터디 설정"
          >
            <Settings className="h-5 w-5" />
          </button>
          <button
            onClick={onInviteClick}
            className="text-muted-foreground hover:text-foreground rounded p-1 transition-colors"
            aria-label="초대"
          >
            <UserPlus className="h-5 w-5" />
          </button>
        </div>
      </div>

      {/* 기본 정보 */}
      <div className="text-muted-foreground mb-1 flex items-center gap-4 text-sm">
        <span>방장: {ownerLabel}</span>
        <span>
          멤버 {studyDetail.memberCount}/{studyDetail.maxMembers}명
        </span>
      </div>
      {studyDetail.description && (
        <p className="text-muted-foreground mb-3 text-sm">{studyDetail.description}</p>
      )}

      {/* 멤버 목록 */}
      <div className="border-t pt-3">
        <p className="text-muted-foreground mb-1 text-xs font-medium uppercase tracking-wide">멤버 목록</p>
        <div className="divide-y">
          {studyDetail.members.map((member) => (
            <MemberRow key={member.userAccountId} member={member} />
          ))}
        </div>
      </div>
    </div>
  );
}
