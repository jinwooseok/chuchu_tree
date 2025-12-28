import type { Metadata } from 'next';
import './globals.css';
import Providers from '@/lib/providers';
import localFont from 'next/font/local';

const paperlogy = localFont({
  src: [
    {
      path: './fonts/Paperlogy-4Regular-sub.woff2',
      weight: '400',
      style: 'normal',
    },
    {
      path: './fonts/Paperlogy-6SemiBold.woff2',
      weight: '600',
      style: 'normal',
    },
  ],
  variable: '--font-paperlogy',
  display: 'swap',
  adjustFontFallback: 'Arial',
});

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
      <body className={`${paperlogy.variable} antialiased`}>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
