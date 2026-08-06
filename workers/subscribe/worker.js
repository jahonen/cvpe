/**
 * CVPE subscribe proxy — Cloudflare Worker
 *
 * Holds the SendGrid API key server-side so the static site never ships it.
 * Deploy: Cloudflare dashboard → Workers & Pages → create Worker, paste this
 * file. Add secret SENDGRID_API_KEY (restricted key: Marketing → Contacts
 * scope only). Attach custom domain api.cvpe.eu (Settings → Domains & Routes)
 * — this proxies only that subdomain; apex and www stay DNS-only for
 * DanubeData certificate issuance.
 *
 * Endpoint: POST https://api.cvpe.eu/subscribe  body: {"email": "..."}
 */

const ALLOWED_ORIGINS = [
  'https://cvpe.eu',
  'https://www.cvpe.eu',
];

function corsHeaders(request) {
  const origin = request.headers.get('Origin') || '';
  return {
    'Access-Control-Allow-Origin': ALLOWED_ORIGINS.includes(origin) ? origin : ALLOWED_ORIGINS[0],
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Vary': 'Origin',
  };
}

function json(body, status, cors) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json', ...cors },
  });
}

export default {
  async fetch(request, env) {
    const cors = corsHeaders(request);

    if (request.method === 'OPTIONS') {
      return new Response(null, { status: 204, headers: cors });
    }
    if (request.method !== 'POST') {
      return json({ error: 'Method not allowed' }, 405, cors);
    }

    // Same-origin gate: browsers always send Origin on cross-site POST
    const origin = request.headers.get('Origin') || '';
    if (!ALLOWED_ORIGINS.includes(origin)) {
      return json({ error: 'Forbidden' }, 403, cors);
    }

    let email = '';
    try {
      const body = await request.json();
      email = String(body.email || '').trim().toLowerCase();
    } catch {
      return json({ error: 'Bad request' }, 400, cors);
    }

    if (email.length > 254 || !/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email)) {
      return json({ error: 'Invalid email' }, 400, cors);
    }

    const res = await fetch('https://api.sendgrid.com/v3/marketing/contacts', {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${env.SENDGRID_API_KEY}`,
      },
      body: JSON.stringify({ contacts: [{ email }] }),
    });

    if (!res.ok) {
      return json({ error: 'Upstream error' }, 502, cors);
    }
    return json({ ok: true }, 200, cors);
  },
};
