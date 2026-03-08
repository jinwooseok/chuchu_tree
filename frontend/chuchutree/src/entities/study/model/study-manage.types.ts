export interface Study {
  studyId: number;
  studyName: string;
  ownerUserAccountId: number;
  ownerBjAccountId: string;
  ownerUserCode: string;
  description: string;
  maxMembers: number;
  memberCount: number;
  createdAt: string;
}

export interface SearchedUser {
  userAccountId: number;
  bjAccountId: string;
  userCode: string;
  profileImageUrl: string | null;
}

export interface SearchedStudy {
  studyId: number;
  studyName: string;
  ownerBjAccountId: string;
  ownerUserCode: string;
  ownerProfileImageUrl: string | null;
  memberCount: number;
}

export interface CreateStudyRequest {
  studyName: string;
  description: string;
  maxMembers: number;
  inviteeUserAccountIds: number[];
}

export interface PendingInvitationItem {
  invitationId: number;
  studyId: number;
  studyName: string;
  inviterUserAccountId: number;
  inviterBjAccountId: string;
  inviterUserCode: string;
  status: string;
  createdAt: string;
  inviterProfileImageUrl: string;
}

export interface PendingApplicationItem {
  applicationId: number;
  studyId: number;
  studyName: string;
  ownerUserAccountId: number;
  ownerBjAccountId: string;
  ownerUserCode: string;
  status: string;
  message: string;
  createdAt: string;
  ownerProfileImageUrl: string;
}

export interface PendingRequests {
  invitations: PendingInvitationItem[];
  applications: PendingApplicationItem[];
}
