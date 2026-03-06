import { Tags } from '@/entities/calendar';
import { TierKey, TierNumKey } from '@/shared/constants/tierSystem';

export interface StudyProblemSolveInfo {
  userAccountId: number;
  bjAccountId: string;
  userCode: string;
  solved: boolean;
  solveDate: string;
}

export interface StudyProblem {
  studyProblemId: number;
  problemId: number;
  problemTitle: string;
  problemTierLevel: TierNumKey;
  problemTierName: TierKey;
  problemClassLevel: number;
  tags: Tags[];
  representativeTag: { tagId: number; tagCode: string; tagDisplayName: string } | null;
  solveInfo: StudyProblemSolveInfo[];
}

export interface StudyMonthlyData {
  targetDate: string;
  problems: StudyProblem[];
}

export interface StudyCalendar {
  monthlyData: StudyMonthlyData[];
}

export interface AssignAllProblemsRequest {
  problemId: number;
  targetDate: string;
}

export interface AssignIndividualProblemsRequest {
  problemId: number;
  assignments: { userAccountId: number; targetDate: string }[];
}
