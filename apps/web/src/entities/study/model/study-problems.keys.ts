export const studyProblemsKeys = {
  all: ['study-problems'] as const,
  lists: () => ['study-problems', 'list'] as const,
  list: (studyId: number, year: number, month: number) =>
    ['study-problems', 'list', { studyId, year, month }] as const,
};
