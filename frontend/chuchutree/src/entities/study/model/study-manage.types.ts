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
  memberCount: number;
}

export interface CreateStudyRequest {
  studyName: string;
  description: string;
  maxMembers: number;
  inviteeUserAccountIds: number[];
}
