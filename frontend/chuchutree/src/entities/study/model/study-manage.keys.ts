export const studyKeys = {
  all: ['study'] as const,
  myList: () => [...studyKeys.all, 'myList'] as const,
  validateName: (name: string) => [...studyKeys.all, 'validateName', name] as const,
  searchUsers: (keyword: string) => [...studyKeys.all, 'searchUsers', keyword] as const,
  searchStudies: (keyword: string) => [...studyKeys.all, 'searchStudies', keyword] as const,
};
