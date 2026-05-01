export const studyDetailKeys = {
  all: ['studyDetail'] as const,
  detail: (studyId: number) => [...studyDetailKeys.all, 'detail', studyId] as const,
  invitations: (studyId: number) => [...studyDetailKeys.all, 'invitations', studyId] as const,
  applications: (studyId: number) => [...studyDetailKeys.all, 'applications', studyId] as const,
};
