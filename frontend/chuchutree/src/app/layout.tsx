import type { Metadata } from 'next';
import './globals.css';
import Providers from '@/lib/providers';
import localFont from 'next/font/local';
import Script from 'next/script';

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
  title: '알고리즘 캘린더 ChuChuTree - 개인 맞춤형 백준 문제 추천',
  description:
    '백준과 solved.ac 데이터를 분석해 당신에게 딱 맞는 알고리즘 문제를 추천합니다. 알고리즘 유형별 분석, 학습 기록 캘린더를 한눈에 확인하세요. 코딩테스트 준비와 알고리즘 실력 향상을 위한 개인 맞춤형 학습 서비스입니다.',
  keywords: [
    'chuchu',
    '츄츄트리',
    '백준 문제 추천',
    'solved.ac',
    '알고리즘 추천',
    '알고리즘 캘린더',
    '알고리즘 기록',
    '코딩테스트 준비',
    'PS 공부',
    '알고리즘 공부 순서',
    '알고리즘 유형 추천',
    '알고리즘 커리큘럼',
    '프로그래밍 학습',
    '알고리즘 대시보드',
  ],
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

        {/* JSON-LD 구조화된 데이터 */}
        <Script
          id="schema-website"
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify({
              '@context': 'https://schema.org',
              '@type': 'WebSite',
              name: 'ChuChuTree',
              alternateName: '츄츄트리',
              url: 'https://chuchu-tree.duckdns.org',
              description: '백준과 solved.ac 데이터를 분석해 개인 맞춤형 알고리즘 문제를 추천하는 학습 캘린더 서비스',
              inLanguage: 'ko-KR',
            }),
          }}
        />

        <Script
          id="schema-software"
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify({
              '@context': 'https://schema.org',
              '@type': 'SoftwareApplication',
              name: 'ChuChuTree',
              applicationCategory: 'EducationalApplication',
              offers: {
                '@type': 'Offer',
                price: '0',
                priceCurrency: 'KRW',
              },
              operatingSystem: 'Web',
              description: '알고리즘 유형별 분석, 학습 기록 캘린더, 개인 맞춤형 문제 추천 기능을 제공하는 백준 학습 도우미',
            }),
          }}
        />
      </body>
    </html>
  );
}
