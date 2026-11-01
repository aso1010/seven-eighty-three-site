// /memo/* — the sentinel at the door of the Communal Foundation memo.
// The page and PDF live inside this Function's bundle, never as static files, so nothing under /memo/
// is served unless the passcode clears. If MEMO_PASSCODE is unset, the door stays shut (503).
// Setup: Cloudflare Pages > Settings > Variables and Secrets, add MEMO_PASSCODE as a Secret (Production).
// Deploy with Wrangler or Git: dashboard drag-and-drop does not run Functions.

import { PAGE, GATE, PDF, PDF_NAME } from './_payload.js';

const BASE = '/memo/communal-foundation/';
const COOKIE = 'memo_cf';
const TTL = 60 * 60 * 12; // seconds a cleared visitor stays cleared

const HEADERS = {
  'cache-control': 'no-store, private',
  'x-robots-tag': 'noindex, nofollow, noarchive, nosnippet',
  'referrer-policy': 'no-referrer',
  'x-content-type-options': 'nosniff',
  'x-frame-options': 'DENY',
  'content-security-policy': "default-src 'none'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src https://fonts.gstatic.com; img-src 'self' data:; form-action 'self'; frame-ancestors 'none'; base-uri 'none'",
};

const enc = new TextEncoder();

async function digest(secret, msg) {
  const key = await crypto.subtle.importKey('raw', enc.encode(secret), { name: 'HMAC', hash: 'SHA-256' }, false, ['sign']);
  return new Uint8Array(await crypto.subtle.sign('HMAC', key, enc.encode(msg)));
}

function same(a, b) {
  if (a.length !== b.length) return false;
  let d = 0;
  for (let i = 0; i < a.length; i++) d |= a[i] ^ b[i];
  return d === 0;
}

const hex = (bytes) => Array.from(bytes, (x) => x.toString(16).padStart(2, '0')).join('');

async function seal(secret, exp) {
  return hex(await digest(secret, `${BASE}${exp}`));
}

async function cleared(request, secret) {
  const m = (request.headers.get('cookie') || '').match(new RegExp(`(?:^|;\\s*)${COOKIE}=(\\d+)\\.([0-9a-f]{64})`));
  if (!m || Number(m[1]) < Date.now() / 1000) return false;
  return same(enc.encode(await seal(secret, m[1])), enc.encode(m[2]));
}

const html = (body, status = 200, extra = {}) =>
  new Response(body, { status, headers: { ...HEADERS, 'content-type': 'text/html; charset=utf-8', ...extra } });

const gate = (wrong) =>
  html(GATE.replace('<!--note-->', wrong ? '      <p class="gate-note" role="alert">Passcode not recognized.</p>' : ''), wrong ? 401 : 200);

export async function onRequest({ request, env }) {
  const secret = env.MEMO_PASSCODE;
  if (!secret) return new Response('Closed.', { status: 503, headers: { ...HEADERS, 'content-type': 'text/plain' } });

  const { pathname } = new URL(request.url);

  if (pathname === BASE.slice(0, -1)) return new Response(null, { status: 308, headers: { ...HEADERS, location: BASE } });

  if (pathname === BASE && request.method === 'POST') {
    let passcode = '';
    try { passcode = String((await request.formData()).get('passcode') || '').slice(0, 256); } catch {}
    const ok = same(await digest(secret, passcode), await digest(secret, secret));
    if (!ok) return gate(true);
    const exp = String(Math.floor(Date.now() / 1000) + TTL);
    return new Response(null, {
      status: 303,
      headers: {
        ...HEADERS,
        location: BASE,
        'set-cookie': `${COOKIE}=${exp}.${await seal(secret, exp)}; Path=${BASE}; Max-Age=${TTL}; HttpOnly; Secure; SameSite=Lax`,
      },
    });
  }

  if (request.method !== 'GET' && request.method !== 'HEAD') return new Response(null, { status: 405, headers: { ...HEADERS, allow: 'GET, HEAD, POST' } });

  if (pathname === BASE) return (await cleared(request, secret)) ? html(PAGE) : gate(false);

  if (pathname === BASE + PDF_NAME) {
    if (!(await cleared(request, secret))) return new Response(null, { status: 303, headers: { ...HEADERS, location: BASE } });
    return new Response(Uint8Array.from(atob(PDF), (c) => c.charCodeAt(0)), {
      headers: { ...HEADERS, 'content-type': 'application/pdf', 'content-disposition': `attachment; filename="${PDF_NAME}"` },
    });
  }

  return new Response('Not found.', { status: 404, headers: { ...HEADERS, 'content-type': 'text/plain' } });
}
