export const noticeKeys = {
  all: ['notices'] as const,
  list: () => [...noticeKeys.all, 'list'] as const,
};
