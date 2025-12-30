import { AppSidebar } from '@/widgets/app-sidebar';
import { SidebarInset, SidebarProvider } from '@/components/ui/sidebar';

export default function MainLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <SidebarProvider defaultOpen={false}>
      <AppSidebar />
      <SidebarInset>{children}</SidebarInset>
    </SidebarProvider>
  );
}
