// Same-origin proxy from the Vercel deployment to the Render API.
// The browser only ever talks to the domain it loaded the page from.
const ORIGIN = (process.env.EKASUTRA_API_ORIGIN || '').replace(/\/+$/, '');

module.exports = async function handler(req, res) {
  res.setHeader('Cache-Control', 'no-store');

  if (!ORIGIN) {
    res.status(503).json({ detail: 'Proxy is not configured: set EKASUTRA_API_ORIGIN in Vercel.' });
    return;
  }

  const raw = req.query.path;
  const parts = Array.isArray(raw) ? raw : [raw].filter(Boolean);
  if (!parts.length || parts.some((p) => !/^[A-Za-z0-9_-]+$/.test(p))) {
    res.status(400).json({ detail: 'Bad API path' });
    return;
  }

  const query = new URL(req.url, 'http://local').search;
  const target = `${ORIGIN}/api/${parts.map(encodeURIComponent).join('/')}${query}`;

  const headers = { accept: 'application/json' };
  if (req.headers['content-type']) headers['content-type'] = req.headers['content-type'];
  if (req.headers['x-demo-role']) headers['x-demo-role'] = req.headers['x-demo-role'];

  const init = {
    method: req.method,
    headers,
    redirect: 'manual',
    signal: AbortSignal.timeout(55000),
  };
  if (req.method !== 'GET' && req.method !== 'HEAD' && req.body != null) {
    init.body = typeof req.body === 'string' ? req.body : JSON.stringify(req.body);
  }

  try {
    const upstream = await fetch(target, init);
    const body = Buffer.from(await upstream.arrayBuffer());
    res.status(upstream.status);
    const type = upstream.headers.get('content-type');
    if (type) res.setHeader('Content-Type', type);
    res.send(body);
  } catch (err) {
    res.status(502).json({ detail: 'API is unreachable', upstream: err.name });
  }
};
