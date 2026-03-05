import { ApiResponse } from '@/shared/types/api';
import { Study, SearchedUser, CreateStudyRequest } from '../model/types';
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
  createStudy: async (body: CreateStudyRequest): Promise<void> => {
    await axiosInstance.post('/studies', body);
  },
};
