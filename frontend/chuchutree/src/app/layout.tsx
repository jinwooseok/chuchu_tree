import type { Metadata } from 'next';
import './globals.css';
import Providers from '@/lib/providers';

export const metadata: Metadata = {
  title: 'ChuChuTree',
  description: 'ChuChuTree Algorithm Calendar',
  icons: {
    icon: '/icon.png',
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
