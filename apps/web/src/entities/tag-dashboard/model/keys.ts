export const tagDashboardKeys = {
  all: ['tagDashboard'] as const,
  dashboard: () => [...tagDashboardKeys.all, 'dashboard'] as const,
  detail: (code: string) => [...tagDashboardKeys.all, 'detail', code] as const,
};
