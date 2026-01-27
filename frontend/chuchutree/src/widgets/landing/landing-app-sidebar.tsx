import { useLandingUser } from '@/features/landing';
import { AppSidebarInset } from '@/features/sidebar';

export function LandingAppSidebar() {
  const user = useLandingUser();
  return <AppSidebarInset user={user} isLanding={true} />;
}
