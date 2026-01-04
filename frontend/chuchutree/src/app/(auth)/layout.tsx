export default function AuthLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return <div className="bg-background flex h-screen w-screen items-center justify-center p-4">{children}</div>;
}
