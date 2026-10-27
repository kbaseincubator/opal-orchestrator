// Same-origin proxy to the backend API.
//
// The browser calls /api/<path> on the frontend's own origin, and this handler
// forwards the request to the backend named by the API_URL environment variable.
// API_URL is read at request time, so the same image works in any environment
// (docker-compose, Rancher, local dev) by setting that variable on the container.

import type { NextRequest } from 'next/server';

export const dynamic = 'force-dynamic';

const DEFAULT_API_URL = 'http://localhost:8000';

// Hop-by-hop or transport-specific headers that must not be forwarded verbatim.
const STRIP_REQUEST_HEADERS = ['host', 'connection', 'content-length', 'accept-encoding'];
const STRIP_RESPONSE_HEADERS = ['content-encoding', 'content-length', 'transfer-encoding', 'connection'];

function apiBase(): string {
  return (process.env.API_URL || DEFAULT_API_URL).replace(/\/+$/, '');
}

type Context = { params: Promise<{ path: string[] }> };

async function proxy(req: NextRequest, ctx: Context): Promise<Response> {
  const { path } = await ctx.params;
  const target = `${apiBase()}/${path.map(encodeURIComponent).join('/')}${req.nextUrl.search}`;

  const headers = new Headers(req.headers);
  for (const h of STRIP_REQUEST_HEADERS) headers.delete(h);

  const hasBody = req.method !== 'GET' && req.method !== 'HEAD';
  const init: RequestInit & { duplex?: 'half' } = {
    method: req.method,
    headers,
    redirect: 'manual',
    cache: 'no-store',
  };
  if (hasBody) {
    // Stream the body through untouched (JSON and multipart uploads alike).
    init.body = req.body;
    init.duplex = 'half';
  }

  let upstream: Response;
  try {
    upstream = await fetch(target, init);
  } catch (error) {
    console.error(`[api proxy] ${req.method} ${target} failed:`, error);
    return Response.json(
      { detail: 'Backend API is unreachable' },
      { status: 502 }
    );
  }

  const resHeaders = new Headers(upstream.headers);
  for (const h of STRIP_RESPONSE_HEADERS) resHeaders.delete(h);

  return new Response(upstream.body, {
    status: upstream.status,
    statusText: upstream.statusText,
    headers: resHeaders,
  });
}

export {
  proxy as GET,
  proxy as POST,
  proxy as PUT,
  proxy as PATCH,
  proxy as DELETE,
  proxy as HEAD,
  proxy as OPTIONS,
};
