import { AppSidebar } from '@/widgets/app-sidebar';

export default function MainLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <>
      <AppSidebar />
      {children}
    </>
  );
}
