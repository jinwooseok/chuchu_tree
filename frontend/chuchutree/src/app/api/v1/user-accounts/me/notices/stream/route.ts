import { NextRequest } from 'next/server';

export const dynamic = 'force-dynamic';

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'https://chuchu-tree-dev.duckdns.org';

export async function GET(req: NextRequest) {
  const accessToken = req.cookies.get('access_token')?.value;
  const refreshToken = req.cookies.get('refresh_token')?.value;

  const cookieHeader = [
    accessToken ? `access_token=${accessToken}` : '',
    refreshToken ? `refresh_token=${refreshToken}` : '',
  ]
    .filter(Boolean)
    .join('; ');

  const res = await fetch(`${BACKEND_URL}/api/v1/user-accounts/me/notices/stream`, {
    cache: 'no-store',
    headers: {
      Cookie: cookieHeader,
      Accept: 'text/event-stream',
      'Cache-Control': 'no-cache',
    },
  });

  if (!res.ok || !res.body) {
    return new Response(null, { status: res.status });
  }

  return new Response(res.body, {
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache, no-transform',
      'X-Accel-Buffering': 'no',
      Connection: 'keep-alive',
    },
  });
}
