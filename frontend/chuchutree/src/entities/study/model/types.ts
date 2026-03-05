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
}

export interface CreateStudyRequest {
  studyName: string;
  description: string;
  maxMembers: number;
  inviteeUserAccountIds: number[];
}
