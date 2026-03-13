import { NoticeCategory } from '@/entities/notice';

export const STUDY_CATEGORIES: NoticeCategory[] = ['STUDY_INVITATION', 'STUDY_APPLICATION', 'STUDY_PROBLEM'];

export const PERSONAL_CATEGORIES: NoticeCategory[] = ['USER_PROBLEM', 'USER_TIER'];

export const ANNOUNCEMENT_CATEGORIES: NoticeCategory[] = ['SYSTEM_ANNOUNCEMENT'];

export type NoticeTab = 'study' | 'personal' | 'announcement';
