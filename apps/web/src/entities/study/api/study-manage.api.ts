import { ApiResponse } from '@/shared/types/api';
import { Study, SearchedUser, SearchedStudy, CreateStudyRequest, PendingRequests } from '../model/study-manage.types';
import { axiosInstance } from '@/lib/axios';

export const studyApi = {
  getMyStudies: async (): Promise<Study[]> => {
    const { data } = await axiosInstance.get<ApiResponse<{ studies: Study[] }>>('/user-accounts/me/studies');
    return data.data.studies;
  },
  validateStudyName: async (name: string): Promise<{ available: boolean }> => {
    const { data } = await axiosInstance.get<ApiResponse<{ available: boolean }>>('/studies/validate-name', {
      params: { name },
    });
    return data.data;
  },
  searchUsers: async (keyword: string): Promise<SearchedUser[]> => {
    const { data } = await axiosInstance.get<ApiResponse<{ users: SearchedUser[] }>>('/user-accounts/search', {
      params: { keyword, limit: 5 },
    });
    return data.data.users;
  },
  createStudy: async (body: CreateStudyRequest): Promise<Study> => {
    const { data } = await axiosInstance.post<ApiResponse<Study>>('/studies', body);
    return data.data;
  },
  searchStudies: async (keyword: string): Promise<SearchedStudy[]> => {
    const { data } = await axiosInstance.get<ApiResponse<{ studies: SearchedStudy[] }>>('/studies/search', {
      params: { keyword, limit: 5 },
    });
    return data.data.studies;
  },
  applyStudy: async (studyId: number): Promise<void> => {
    await axiosInstance.post(`/studies/${studyId}/applications`, { message: '가입신청' });
  },
  cancelApplyStudy: async (studyId: number): Promise<void> => {
    await axiosInstance.delete(`/studies/${studyId}/applications/me`);
  },
  getMyPendingRequests: async (): Promise<PendingRequests> => {
    const { data } = await axiosInstance.get<ApiResponse<PendingRequests>>('/user-accounts/me/pending-requests');
    return data.data;
  },
  acceptInvitation: async (invitationId: number): Promise<void> => {
    await axiosInstance.post(`/user-accounts/me/invitations/${invitationId}/accept`);
  },
  rejectInvitation: async (invitationId: number): Promise<void> => {
    await axiosInstance.post(`/user-accounts/me/invitations/${invitationId}/reject`);
  },
};
