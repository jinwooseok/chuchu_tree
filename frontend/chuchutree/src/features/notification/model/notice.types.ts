import { WillSolveProblems, SolvedProblems } from '@/entities/calendar/model/calendar.types';
import { TierNumKey } from '@/shared/constants/tierSystem';

export type NoticeCategory =
  | 'study-invitation-status'
  | 'study-application-status'
  | 'study-problems-status'
  | 'user-problems-status'
  | 'user-tier-status'
  | 'system-announcement'
  | 'study-received-invitation'
  | 'study-received-application';

export type NoticeStatusValue = 'pending' | 'accepted' | 'rejected';

export type NoticeTab = 'study' | 'personal' | 'announcement';

interface BaseNotice {
  id: number;
  category: NoticeCategory;
  isRead: boolean;
  createdAt: string; // ISO 8601
}

export interface StudyInvitationNotice extends BaseNotice {
  category: 'study-invitation-status';
  studyName: string;
  userId: string; // bjAccountId
  userCode: string; // defaultCode
  status: NoticeStatusValue;
}

export interface StudyApplicationNotice extends BaseNotice {
  category: 'study-application-status';
  studyName: string;
  status: NoticeStatusValue;
}

export interface StudyProblemsNotice extends BaseNotice {
  category: 'study-problems-status';
  studyName: string;
  problem: WillSolveProblems;
  calendarDate: string; // YYYY-MM-DD
}

export interface UserProblemsNotice extends BaseNotice {
  category: 'user-problems-status';
  problem: SolvedProblems;
  date: string; // YYYY-MM-DD
}

export interface UserTierNotice extends BaseNotice {
  category: 'user-tier-status';
  tierLevel: TierNumKey;
}

export interface SystemAnnouncementNotice extends BaseNotice {
  category: 'system-announcement';
  text: string;
}

export interface StudyReceivedInvitationNotice extends BaseNotice {
  category: 'study-received-invitation';
  studyName: string;
  inviterUserId: string; // bjAccountId
  inviterUserCode: string; // defaultCode
  status: NoticeStatusValue;
}

export interface StudyReceivedApplicationNotice extends BaseNotice {
  category: 'study-received-application';
  studyName: string;
  applicantUserId: string; // bjAccountId
  applicantUserCode: string; // defaultCode
  status: NoticeStatusValue;
}

export type Notice =
  | StudyInvitationNotice
  | StudyApplicationNotice
  | StudyProblemsNotice
  | UserProblemsNotice
  | UserTierNotice
  | SystemAnnouncementNotice
  | StudyReceivedInvitationNotice
  | StudyReceivedApplicationNotice;
