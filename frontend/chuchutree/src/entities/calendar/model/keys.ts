export const calendarKeys = {
  all: ['calendar'] as const,
  lists: () => [...calendarKeys.all, 'list'] as const,
  list: (year: number, month: number) => [...calendarKeys.lists(), { year, month }] as const,
  searches: () => [...calendarKeys.all, 'search'] as const,
  search: (keyword: string) => [...calendarKeys.searches(), { keyword }] as const,
};
