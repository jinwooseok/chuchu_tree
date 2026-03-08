import { ApiResponse } from '@/shared/types/api';
import { StudyCalendar, AssignAllProblemsRequest, AssignIndividualProblemsRequest } from '../model/study-problems.types';
import { axiosInstance } from '@/lib/axios';

export const studyProblemsApi = {
  getStudyProblems: async (studyId: number, year: number, month: number): Promise<StudyCalendar> => {
    const { data } = await axiosInstance.get<ApiResponse<StudyCalendar>>(`/studies/${studyId}/problems`, {
      params: { year, month },
    });
    return data.data;
  },

  assignProblemToAll: async (studyId: number, body: AssignAllProblemsRequest): Promise<void> => {
    await axiosInstance.post(`/studies/${studyId}/problems/all`, body);
  },

  assignProblemToIndividuals: async (studyId: number, body: AssignIndividualProblemsRequest): Promise<void> => {
    await axiosInstance.post(`/studies/${studyId}/problems`, body);
  },

  deleteStudyProblem: async (studyId: number, studyProblemId: number): Promise<void> => {
    await axiosInstance.delete(`/studies/${studyId}/problems/${studyProblemId}`);
  },
};
