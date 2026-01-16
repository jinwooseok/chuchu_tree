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
  title: 'ChuChuTree | 알고리즘 캘린더',
  description: 'ChuChuTree Algorithm Calendar',
  keywords: ['ChuChuTree', 'Algorithm', '츄츄트리', '츄츄', '알고리즘 기록', '백준', 'solved.ac', '알고리즘 추천'],
  metadataBase: new URL('https://chuchu-tree.duckdns.org'),
  alternates: {
    canonical: '/',
  },
  openGraph: {
    type: 'website',
    locale: 'ko_KR',
    url: 'https://chuchu-tree.duckdns.org',
    title: 'ChuChuTree',
    description: 'ChuChuTree Algorithm Calendar',
    siteName: 'ChuChuTree',
    images: [
      {
        url: '/opengraph/opengraph_630.png',
        width: 1200,
        height: 630,
        alt: 'ChuChuTree Algorithm Calendar open-graph 630',
      },
      {
        url: '/opengraph/opengraph_1200.png',
        width: 1200,
        height: 1200,
        alt: 'ChuChuTree Algorithm Calendar open-graph 1200',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'ChuChuTree',
    description: 'ChuChuTree Algorithm Calendar',
    images: ['/opengraph/opengraph_630.png'],
  },
  robots: {
    index: true, // 검색결과에 포함
    follow: true, // 링크 내려가기 가능
    nocache: false, // 캐시 허용
    googleBot: {
      index: true, // 구글전용 동일함
      follow: true, // 동일함
      noimageindex: false, // 이미지도 포함
      'max-image-preview': 'large', // 큰이미지 허용
      'max-snippet': -1, // 텍스트미리보기제한없음
    },
  },
  icons: {
    icon: '/icon.svg',
  },
  verification: {
    google: 'uX2sSiFJCH4Ou0YrgWMwlhPga-av58R9NcPBEh78NZ8',
    other: {
      'naver-site-verification': 'e5832af048f20a958b40ba905763297546a02a90',
    },
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ko" suppressHydrationWarning>
      <body className={`${paperlogy.variable} antialiased`}>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
