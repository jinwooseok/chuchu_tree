import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  /* config options here */
  reactCompiler: true,
  output: 'standalone',
  experimental: {
    proxyTimeout: 120000, // 120초 (기본값 30초)
  },
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'coffeebara-storage.duckdns.org',
      },
    ],
  },

  // 개발 환경에서 백엔드 API를 프록시
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${process.env.NEXT_PUBLIC_BACKEND_URL || 'https://chuchu-tree-dev.duckdns.org'}/api/:path*`,
      },
    ];
  },
};

export default nextConfig;
