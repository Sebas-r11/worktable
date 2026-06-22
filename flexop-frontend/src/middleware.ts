import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

const BACKEND_INTERNAL =
  process.env.BACKEND_INTERNAL_URL ?? 'http://127.0.0.1:8000';

/**
 * Proxy /api/* → Django conservando la barra final (DRF la exige).
 * Next.js suele normalizar URLs sin "/" y rompe POST (APPEND_SLASH).
 */
export function middleware(request: NextRequest) {
  const { pathname, search } = request.nextUrl;

  if (!pathname.startsWith('/api/')) {
    return NextResponse.next();
  }

  let apiPath = pathname;
  const looksLikeFile = /\.[a-zA-Z0-9]+$/.test(pathname);
  if (!looksLikeFile && !apiPath.endsWith('/')) {
    apiPath = `${apiPath}/`;
  }

  const target = new URL(`${apiPath}${search}`, BACKEND_INTERNAL);
  return NextResponse.rewrite(target);
}

export const config = {
  matcher: '/api/:path*',
};
