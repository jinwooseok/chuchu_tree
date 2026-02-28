'use client';

import { CalendarPlus, CheckCheck, ClipboardList, Megaphone, TrendingUp, UserCheck, UserPlus, Users } from 'lucide-react';
import { NoticeCategory, NoticeStatusValue } from './notice.types';

export const STATUS_CONFIG: Record<NoticeStatusValue, { label: string; className: string }> = {
  pending: { label: '대기 중', className: 'text-muted-foreground' },
  accepted: { label: '수락됨', className: 'text-advanced-bg' },
  rejected: { label: '거절됨', className: 'text-excluded-bg' },
};

export const CATEGORY_LABEL: Record<NoticeCategory, string> = {
  'study-received-invitation': '스터디 초대 받음',
  'study-received-application': '가입 신청 받음',
  'study-invitation-status': '스터디 초대',
  'study-application-status': '가입 신청',
  'study-problems-status': '문제 등록',
  'user-problems-status': '문제 업데이트',
  'user-tier-status': '티어 상승',
  'system-announcement': '공지사항',
};

export const CATEGORY_ICON: Record<NoticeCategory, React.ReactNode> = {
  'study-received-invitation': <UserPlus className="mt-0.5 h-4 w-4 shrink-0" />,
  'study-received-application': <UserCheck className="mt-0.5 h-4 w-4 shrink-0" />,
  'study-invitation-status': <Users className="mt-0.5 h-4 w-4 shrink-0" />,
  'study-application-status': <ClipboardList className="mt-0.5 h-4 w-4 shrink-0" />,
  'study-problems-status': <CalendarPlus className="mt-0.5 h-4 w-4 shrink-0" />,
  'user-problems-status': <CheckCheck className="mt-0.5 h-4 w-4 shrink-0" />,
  'user-tier-status': <TrendingUp className="mt-0.5 h-4 w-4 shrink-0" />,
  'system-announcement': <Megaphone className="mt-0.5 h-4 w-4 shrink-0" />,
};
