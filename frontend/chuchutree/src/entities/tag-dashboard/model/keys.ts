export const tagDashboardKeys = {
  all: ['tagDashboard'] as const,
  dashboard: () => [...tagDashboardKeys.all, 'dashboard'] as const,
};
