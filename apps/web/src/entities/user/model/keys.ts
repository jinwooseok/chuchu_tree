export const userKeys = {
  all: ['user'] as const,
  me: () => [...userKeys.all, 'me'] as const,
};

export const streakKeys = {
  all: ['streak'] as const,
  lists: () => [...streakKeys.all, 'list'] as const,
  list: (startDate: string, endDate: string) => [...streakKeys.lists(), { startDate, endDate }] as const,
};
