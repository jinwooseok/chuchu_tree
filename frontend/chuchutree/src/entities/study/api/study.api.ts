import { ApiResponse } from '@/shared/types/api';
import { Study } from '../model/types';
import { axiosInstance } from '@/lib/axios';

export const studyApi = {
  getMyStudies: async (): Promise<Study[]> => {
    const { data } = await axiosInstance.get<ApiResponse<{ studies: Study[] }>>('/user-accounts/me/studies');
    return data.data.studies;
  },
};
