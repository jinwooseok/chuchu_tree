'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { studyDetailApi } from '../api/study-detail.api';
import { studyDetailKeys } from './study-detail.keys';
import { studyKeys } from './study-manage.keys';
import { UpdateStudyRequest } from './study-detail.types';
import { UseMutationCallback } from '@/shared/types/api';

// ── 기본 정보 조회 ──────────────────────────────────────────────

export const useStudyDetail = (studyId: number) => {
  return useQuery({
    queryKey: studyDetailKeys.detail(studyId),
    queryFn: () => studyDetailApi.getStudyDetail(studyId),
    enabled: studyId > 0,
  });
};

// ── 스터디 정보 수정 (방장전용) ──────────────────────────────────

export const useUpdateStudy = (studyId: number, callbacks?: UseMutationCallback) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (body: UpdateStudyRequest) => studyDetailApi.updateStudy(studyId, body),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: studyDetailKeys.detail(studyId) });
      callbacks?.onSuccess?.();
    },
    onError: (error) => callbacks?.onError?.(error),
  });
};

// ── 스터디 탈퇴 ─────────────────────────────────────────────────

export const useLeaveStudy = (callbacks?: UseMutationCallback) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (studyId: number) => studyDetailApi.leaveStudy(studyId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: studyKeys.myList() });
      callbacks?.onSuccess?.();
    },
    onError: (error) => callbacks?.onError?.(error),
  });
};

// ── 멤버 강제 퇴장 (방장전용) ───────────────────────────────────

export const useKickMember = (studyId: number, callbacks?: UseMutationCallback) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (memberUserAccountId: number) => studyDetailApi.kickMember(studyId, memberUserAccountId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: studyDetailKeys.detail(studyId) });
      callbacks?.onSuccess?.();
    },
    onError: (error) => callbacks?.onError?.(error),
  });
};

// ── 스터디 삭제 (방장전용) ──────────────────────────────────────

export const useDeleteStudy = (callbacks?: UseMutationCallback) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (studyId: number) => studyDetailApi.deleteStudy(studyId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: studyKeys.myList() });
      callbacks?.onSuccess?.();
    },
    onError: (error) => callbacks?.onError?.(error),
  });
};

// ── 보낸 초대 목록 조회 (방장) ──────────────────────────────────

export const useStudyInvitations = (studyId: number) => {
  return useQuery({
    queryKey: studyDetailKeys.invitations(studyId),
    queryFn: () => studyDetailApi.getStudyInvitations(studyId),
    enabled: studyId > 0,
  });
};

// ── 초대 발송 (방장전용) ────────────────────────────────────────

export const useSendInvitation = (studyId: number, callbacks?: UseMutationCallback) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (inviteeUserAccountId: number) => studyDetailApi.sendInvitation(studyId, inviteeUserAccountId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: studyDetailKeys.detail(studyId) });
      queryClient.invalidateQueries({ queryKey: studyDetailKeys.invitations(studyId) });
      callbacks?.onSuccess?.();
    },
    onError: (error) => callbacks?.onError?.(error),
  });
};

// ── 초대 취소 (방장전용) ────────────────────────────────────────

export const useCancelInvitation = (studyId: number, callbacks?: UseMutationCallback) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (invitationId: number) => studyDetailApi.cancelInvitation(studyId, invitationId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: studyDetailKeys.detail(studyId) });
      queryClient.invalidateQueries({ queryKey: studyDetailKeys.invitations(studyId) });
      callbacks?.onSuccess?.();
    },
    onError: (error) => callbacks?.onError?.(error),
  });
};

// ── 받은 신청 목록 조회 (멤버 권한) ─────────────────────────────

export const useStudyApplications = (studyId: number) => {
  return useQuery({
    queryKey: studyDetailKeys.applications(studyId),
    queryFn: () => studyDetailApi.getStudyApplications(studyId),
    enabled: studyId > 0,
  });
};

// ── 신청 수락 (방장전용) ────────────────────────────────────────

export const useAcceptApplication = (studyId: number, callbacks?: UseMutationCallback) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (applicationId: number) => studyDetailApi.acceptApplication(applicationId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: studyDetailKeys.detail(studyId) });
      queryClient.invalidateQueries({ queryKey: studyDetailKeys.applications(studyId) });
      callbacks?.onSuccess?.();
    },
    onError: (error) => callbacks?.onError?.(error),
  });
};

// ── 신청 거절 (방장전용) ────────────────────────────────────────

export const useRejectApplication = (studyId: number, callbacks?: UseMutationCallback) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (applicationId: number) => studyDetailApi.rejectApplication(applicationId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: studyDetailKeys.detail(studyId) });
      queryClient.invalidateQueries({ queryKey: studyDetailKeys.applications(studyId) });
      callbacks?.onSuccess?.();
    },
    onError: (error) => callbacks?.onError?.(error),
  });
};
