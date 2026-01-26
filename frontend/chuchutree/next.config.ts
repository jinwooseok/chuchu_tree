import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  /* config options here */
  reactCompiler: true,
  output: 'standalone',

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
