import { ApiResponse } from '@/shared/types/api';
import { StudyDetail, UpdateStudyRequest, StudyInvitation, StudyApplication } from '../model/study-detail.types';
import { axiosInstance } from '@/lib/axios';

export const studyDetailApi = {
  getStudyDetail: async (studyId: number): Promise<StudyDetail> => {
    const { data } = await axiosInstance.get<ApiResponse<StudyDetail>>(`/studies/${studyId}`);
    return data.data;
  },

  updateStudy: async (studyId: number, body: UpdateStudyRequest): Promise<void> => {
    await axiosInstance.patch(`/studies/${studyId}`, body);
  },

  leaveStudy: async (studyId: number): Promise<void> => {
    await axiosInstance.post(`/studies/${studyId}/members/leave`);
  },

  kickMember: async (studyId: number, memberUserAccountId: number): Promise<void> => {
    await axiosInstance.delete(`/studies/${studyId}/members/${memberUserAccountId}`);
  },

  deleteStudy: async (studyId: number): Promise<void> => {
    await axiosInstance.delete(`/studies/${studyId}`);
  },

  getStudyInvitations: async (studyId: number): Promise<StudyInvitation[]> => {
    const { data } = await axiosInstance.get<ApiResponse<{ invitations: StudyInvitation[] }>>(`/studies/${studyId}/invitations`);
    return data.data.invitations;
  },

  sendInvitation: async (studyId: number, inviteeUserAccountId: number): Promise<void> => {
    await axiosInstance.post(`/studies/${studyId}/invitations`, { inviteeUserAccountId });
  },

  cancelInvitation: async (studyId: number, invitationId: number): Promise<void> => {
    await axiosInstance.delete(`/studies/${studyId}/invitations/${invitationId}`);
  },

  getStudyApplications: async (studyId: number): Promise<StudyApplication[]> => {
    const { data } = await axiosInstance.get<ApiResponse<{ applications: StudyApplication[] }>>(`/studies/${studyId}/applications`);
    return data.data.applications;
  },

  acceptApplication: async (applicationId: number): Promise<void> => {
    await axiosInstance.post(`/studies/applications/${applicationId}/accept`);
  },

  rejectApplication: async (applicationId: number): Promise<void> => {
    await axiosInstance.post(`/studies/applications/${applicationId}/reject`);
  },
};
