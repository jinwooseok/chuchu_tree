'use client';

import { CalendarPlus, CheckCheck, Megaphone, TrendingUp, UserCheck, UserPlus } from 'lucide-react';
import { NoticeCategory, NoticeCategoryDetail } from '@/entities/notice';

export const STATUS_CONFIG: Record<'PENDING' | 'ACCEPTED' | 'REJECTED', { label: string; className: string }> = {
  PENDING: { label: '대기 중', className: 'text-muted-foreground' },
  ACCEPTED: { label: '수락됨', className: 'text-advanced-bg' },
  REJECTED: { label: '거절됨', className: 'text-excluded-bg' },
};

export const CATEGORY_LABEL: Record<NoticeCategory, string> = {
  STUDY_INVITATION: '스터디 초대',
  STUDY_APPLICATION: '가입 신청',
  STUDY_PROBLEM: '문제 등록',
  USER_PROBLEM: '문제 업데이트',
  USER_TIER: '티어 상승',
  SYSTEM_ANNOUNCEMENT: '공지사항',
};

export const CATEGORY_DETAIL_LABEL: Record<NoticeCategoryDetail, string> = {
  REQUESTED_STUDY_INVITATION: '스터디 초대 받음',
  RESPONSED_STUDY_INVITATION: '스터디 초대 결과',
  REQUESTED_STUDY_APPLICATION: '가입 신청 받음',
  RESPONSED_STUDY_APPLICATION: '가입 신청 결과',
  ASSIGNED_STUDY_PROBLEM: '문제 등록',
  UPDATED_USER_PROBLEM: '문제 업데이트',
  UPDATED_USER_TIER: '티어 상승',
  SYSTEM_ANNOUNCEMENT: '공지사항',
};

export const CATEGORY_ICON: Record<NoticeCategory, React.ReactNode> = {
  STUDY_INVITATION: <UserPlus className="mt-0.5 h-4 w-4 shrink-0" />,
  STUDY_APPLICATION: <UserCheck className="mt-0.5 h-4 w-4 shrink-0" />,
  STUDY_PROBLEM: <CalendarPlus className="mt-0.5 h-4 w-4 shrink-0" />,
  USER_PROBLEM: <CheckCheck className="mt-0.5 h-4 w-4 shrink-0" />,
  USER_TIER: <TrendingUp className="mt-0.5 h-4 w-4 shrink-0" />,
  SYSTEM_ANNOUNCEMENT: <Megaphone className="mt-0.5 h-4 w-4 shrink-0" />,
};
