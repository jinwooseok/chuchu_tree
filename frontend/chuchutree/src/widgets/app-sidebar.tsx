import { useUser } from '@/entities/user';
import { AppSidebarInset } from '@/features/sidebar';

export function AppSidebar() {
  const { data: user } = useUser();
  return <AppSidebarInset user={user}/>;
}
