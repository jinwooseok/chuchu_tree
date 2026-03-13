import { TierNumKey } from '@/shared/constants/tierSystem';

// ─── 대분류 / 소분류 ─────────────────────────────────────────────────────────

export type NoticeCategory = 'STUDY_INVITATION' | 'STUDY_APPLICATION' | 'STUDY_PROBLEM' | 'USER_PROBLEM' | 'USER_TIER' | 'SYSTEM_ANNOUNCEMENT';

export type NoticeCategoryDetail =
  | 'REQUESTED_STUDY_INVITATION'
  | 'RESPONSED_STUDY_INVITATION'
  | 'REQUESTED_STUDY_APPLICATION'
  | 'RESPONSED_STUDY_APPLICATION'
  | 'ASSIGNED_STUDY_PROBLEM'
  | 'UPDATED_USER_PROBLEM'
  | 'UPDATED_USER_TIER'
  | 'SYSTEM_ANNOUNCEMENT';

// ─── content 인터페이스 ────────────────────────────────────────────────────────

// 내가 받은 스터디 초대 알림
export interface RequestedStudyInvitationContent {
  studyId: number;
  studyName: string;
  inviterUserAccountId: string;
  inviterBjAccountId: string;
  inviterUserCode: string;
  profileImageUrl: string;
  status: 'PENDING' | 'ACCEPTED' | 'REJECTED';
}

// 내가 보냈던 스터디 초대의 결과 알림
export interface ResponsedStudyInvitationContent {
  studyId: number;
  studyName: string;
  inviteeUserAccountId: string;
  inviteeBjAccountId: string;
  inviteeUserCode: string;
  profileImageUrl: string;
  status: 'PENDING' | 'ACCEPTED' | 'REJECTED';
}

// 나의 스터디로 온 가입신청 알림
export interface RequestedStudyApplicationContent {
  studyId: number;
  studyName: string;
  applicantUserAccountId: string;
  applicantBjAccountId: string;
  applicantUserCode: string;
  profileImageUrl: string;
  status: 'PENDING' | 'ACCEPTED' | 'REJECTED';
}

// 내가 보냈던 스터디 신청의 결과 알림
export interface ResponsedStudyApplicationContent {
  studyId: number;
  studyName: string;
  ownerUserAccountId: string;
  ownerBjAccountId: string;
  ownerUserCode: string;
  profileImageUrl: string;
  status: 'PENDING' | 'ACCEPTED' | 'REJECTED';
}

// 스터디에 문제가 등록됨 알림
export interface AssignedStudyProblemContent {
  studyId: number;
  studyName: string;
  assignerUserAccountId: string;
  assignerBjAccountId: string;
  assignerUserCode: string;
  profileImageUrl: string;
  assignees: { userAccountId: string; bjAccountId: string; userCode: string; profileImageUrl: string }[];
  problem: { problemId: number; problemTitle: string };
  calendarDate: string; // YYYY-MM-DD
}

// 내가 푼 문제가 등록됨 알림
export interface UpdatedUserProblemContent {
  problemsByDate: { solvedDate: string; problems: { problemId: number; problemTitle: string } }[];
  updatedBy: 'SCHEDULER' | 'DIRECT_REFRESH';
}

// 나의 티어가 상승함 알림
export interface UpdatedUserTierContent {
  tierLevel: TierNumKey;
  updatedBy: 'SCHEDULER' | 'DIRECT_REFRESH';
  updatedDate: string;
}

// 공지사항
export interface SystemAnnouncementContent {
  text: string;
}

export type BaseNoticeContent =
  | RequestedStudyInvitationContent
  | ResponsedStudyInvitationContent
  | RequestedStudyApplicationContent
  | ResponsedStudyApplicationContent
  | AssignedStudyProblemContent
  | UpdatedUserProblemContent
  | UpdatedUserTierContent
  | SystemAnnouncementContent;

// ─── BaseNotice ───────────────────────────────────────────────────────────────

export interface BaseNotice {
  noticeId: number;
  category: NoticeCategory;
  categoryDetail: NoticeCategoryDetail;
  content: BaseNoticeContent;
  message: string;
  isRead: boolean;
  createdAt: string; // ISO 8601
}

// ─── 타입가드 헬퍼 ─────────────────────────────────────────────────────────────

export function isRequestedStudyInvitation(notice: BaseNotice): notice is BaseNotice & { content: RequestedStudyInvitationContent } {
  return notice.categoryDetail === 'REQUESTED_STUDY_INVITATION';
}

export function isResponsedStudyInvitation(notice: BaseNotice): notice is BaseNotice & { content: ResponsedStudyInvitationContent } {
  return notice.categoryDetail === 'RESPONSED_STUDY_INVITATION';
}

export function isRequestedStudyApplication(notice: BaseNotice): notice is BaseNotice & { content: RequestedStudyApplicationContent } {
  return notice.categoryDetail === 'REQUESTED_STUDY_APPLICATION';
}

export function isResponsedStudyApplication(notice: BaseNotice): notice is BaseNotice & { content: ResponsedStudyApplicationContent } {
  return notice.categoryDetail === 'RESPONSED_STUDY_APPLICATION';
}

export function isAssignedStudyProblem(notice: BaseNotice): notice is BaseNotice & { content: AssignedStudyProblemContent } {
  return notice.categoryDetail === 'ASSIGNED_STUDY_PROBLEM';
}

export function isUpdatedUserProblem(notice: BaseNotice): notice is BaseNotice & { content: UpdatedUserProblemContent } {
  return notice.categoryDetail === 'UPDATED_USER_PROBLEM';
}

export function isUpdatedUserTier(notice: BaseNotice): notice is BaseNotice & { content: UpdatedUserTierContent } {
  return notice.categoryDetail === 'UPDATED_USER_TIER';
}

export function isSystemAnnouncement(notice: BaseNotice): notice is BaseNotice & { content: SystemAnnouncementContent } {
  return notice.categoryDetail === 'SYSTEM_ANNOUNCEMENT';
}
