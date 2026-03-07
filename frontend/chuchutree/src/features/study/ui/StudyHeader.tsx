'use client';

import { Settings, UserPlus } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { StudyDetail, StudyMember } from '@/entities/study';
import { UserAvatar } from '@/components/custom/UserAvatar';

interface StudyHeaderProps {
  studyDetail: StudyDetail;
  currentUserAccountId: number;
  onSettingsClick: () => void;
  onInviteClick: () => void;
  isEditing: boolean;
  editDescription: string;
  editMaxMembers: number;
  onEditDescriptionChange: (v: string) => void;
  onEditMaxMembersChange: (v: number) => void;
}

function MemberRow({ member }: { member: StudyMember }) {
  const isOwner = member.role === 'OWNER';
  return (
    <div className="flex items-center justify-between py-1.5">
      <div className="flex items-center gap-2">
        <UserAvatar profileImageUrl={member.profileImageUrl} bjAccountId={member.bjAccountId} userCode={member.userCode} size={24} />
        <span className="text-sm font-medium">
          {member.bjAccountId}#{member.userCode}
        </span>
        {isOwner && <span className="bg-primary/10 text-primary rounded px-1.5 py-0.5 text-xs font-medium">방장</span>}
      </div>
      <span className="text-muted-foreground text-xs">가입일: {member.joinedAt.slice(0, 10)}</span>
    </div>
  );
}

export function StudyHeader({
  studyDetail,
  currentUserAccountId,
  onSettingsClick,
  onInviteClick,
  isEditing,
  editDescription,
  editMaxMembers,
  onEditDescriptionChange,
  onEditMaxMembersChange,
}: StudyHeaderProps) {
  const ownerMember = studyDetail.members.find((m) => m.userAccountId === studyDetail.ownerUserAccountId);
  const ownerLabel = ownerMember ? `${ownerMember.bjAccountId}#${ownerMember.userCode}` : String(studyDetail.ownerUserAccountId);

  return (
    <div className="h-full w-full rounded-lg border p-4">
      {/* 헤더 행: 스터디명 + 아이콘 */}
      <div className="mb-2 flex items-center justify-between">
        <h2 className="truncate text-lg font-bold">{studyDetail.studyName}</h2>
        <div className="flex items-center gap-1">
          <button onClick={onSettingsClick} className="text-muted-foreground hover:text-foreground rounded p-1 transition-colors" aria-label="스터디 설정">
            <Settings className="h-5 w-5" />
          </button>
          <button onClick={onInviteClick} className="text-muted-foreground hover:text-foreground rounded p-1 transition-colors" aria-label="초대">
            <UserPlus className="h-5 w-5" />
          </button>
        </div>
      </div>

      {/* 기본 정보 */}
      <div className="text-muted-foreground mb-2 flex items-center gap-4 text-sm whitespace-nowrap">
        <span className="truncate">방장: {ownerLabel}</span>
        {isEditing ? (
          <div className="flex items-center gap-1">
            <span>멤버 {studyDetail.memberCount}/</span>
            <Input
              type="number"
              min={studyDetail.memberCount}
              max={10}
              value={editMaxMembers}
              onChange={(e) => onEditMaxMembersChange(Math.max(studyDetail.memberCount, Math.min(10, Number(e.target.value))))}
              className="h-6 w-14 px-1 text-xs"
            />
            <span>명</span>
          </div>
        ) : (
          <span>
            멤버 {studyDetail.memberCount}/{studyDetail.maxMembers}명
          </span>
        )}
      </div>

      {/* 설명 */}
      {isEditing ? (
        <Textarea
          value={editDescription}
          onChange={(e) => onEditDescriptionChange(e.target.value)}
          placeholder="스터디 설명을 입력하세요"
          className="mb-3 resize-none text-sm whitespace-nowrap"
          rows={3}
        />
      ) : (
        studyDetail.description && <p className="text-muted-foreground mb-3 text-sm break-all">{studyDetail.description}</p>
      )}

      {/* 멤버 목록 */}
      <div className="border-t pt-3">
        <p className="text-muted-foreground mb-1 text-xs font-medium tracking-wide uppercase">멤버 목록</p>
        <div className="divide-y">
          {studyDetail.members.map((member) => (
            <MemberRow key={member.userAccountId} member={member} />
          ))}
        </div>
      </div>
    </div>
  );
}
