export interface StudyMember {
  userAccountId: number;
  bjAccountId: string;
  userCode: string;
  role: string;
  joinedAt: string;
  profileImageUrl: string | null;
}

export interface PendingInvitation {
  invitationId: number;
  inviteeUserAccountId: number;
  inviteeBjAccountId: string;
  inviteeUserCode: string;
  createdAt: string;
  profileImageUrl: string | null;
}

export interface PendingApplication {
  applicationId: number;
  applicantUserAccountId: number;
  applicantBjAccountId: string;
  applicantUserCode: string;
  createdAt: string;
  profileImageUrl: string | null;
}

export interface StudyDetail {
  studyId: number;
  studyName: string;
  ownerUserAccountId: number;
  description: string;
  maxMembers: number;
  memberCount: number;
  createdAt: string;
  members: StudyMember[];
  pendingInvitations: PendingInvitation[];
  pendingApplications: PendingApplication[];
}

export interface UpdateStudyRequest {
  description: string;
  maxMembers: number;
}

export interface StudyInvitation {
  invitationId: number;
  studyId: number;
  studyName: string;
  inviterUserAccountId: number;
  inviterBjAccountId: string;
  inviterUserCode: string;
  inviterProfileImageUrl: string | null;
  status: 'PENDING' | 'ACCEPTED' | 'REJECTED';
  createdAt: string;
}

export interface StudyApplication {
  applicationId: number;
  studyId: number;
  applicantUserAccountId: number;
  applicantBjAccountId: string;
  applicantUserCode: string;
  applicantProfileImageUrl: string | null;
  status: 'PENDING' | 'ACCEPTED' | 'REJECTED';
  message: string;
  createdAt: string;
}
