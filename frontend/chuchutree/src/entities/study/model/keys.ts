export const studyKeys = {
  all: ['study'] as const,
  myList: () => [...studyKeys.all, 'myList'] as const,
};
