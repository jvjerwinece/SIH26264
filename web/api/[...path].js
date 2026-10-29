// Same-origin proxy from the Vercel deployment to the Render API.
// The browser only ever talks to the domain it loaded the page from.
const ORIGIN = (process.env.EKASUTRA_API_ORIGIN || '').replace(/\/+$/, '');

module.exports = async function handler(req, res) {
  res.setHeader('Cache-Control', 'no-store');

  if (!ORIGIN) {
    res.status(503).json({ detail: 'Proxy is not configured: set EKASUTRA_API_ORIGIN in Vercel.' });
    return;
  }

  // Vercel does not always populate req.query for a catch-all function, so read
  // the path from req.url and fall back to the query object only if it is there.
  const url = new URL(req.url, 'http://local');
  const fromQuery = req.query && req.query.path;
  let parts = Array.isArray(fromQuery) ? fromQuery : fromQuery ? [fromQuery] : [];
  if (!parts.length) {
    let path = url.pathname;
    if (path.startsWith('/api/')) path = path.slice(5);
    else if (path === '/api') path = '';
    else if (path.startsWith('/api')) path = path.slice(4);
    parts = path.split('/').filter(Boolean).map(decodeURIComponent);
  }
  if (!parts.length || parts.some((p) => !/^[A-Za-z0-9_-]+$/.test(p))) {
    res.status(400).json({ detail: 'Bad API path' });
    return;
  }

  const target = `${ORIGIN}/api/${parts.map(encodeURIComponent).join('/')}${url.search}`;

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
