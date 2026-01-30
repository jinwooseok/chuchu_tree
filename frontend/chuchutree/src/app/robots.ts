import { MetadataRoute } from 'next';

export default function robots(): MetadataRoute.Robots {
  const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'https://chuchu-tree.duckdns.org';

  return {
    rules: {
      userAgent: '*',
      allow: '/',
      disallow: ['/chu', '/bj-account'],
    },
    sitemap: `${baseUrl}/sitemap.xml`,
  };
}
