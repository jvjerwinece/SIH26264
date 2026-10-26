const { chromium } = require('playwright');
const { pathToFileURL } = require('url');
const path = require('path');
const fs = require('fs');

const FILE = pathToFileURL(path.resolve(__dirname, '../submission/Ekasutra_v8.html')).href;
const OUT = path.resolve(__dirname, 'artifacts');
const STRICT = process.env.QA_STRICT === '1';

async function launch() {
  const channels = process.env.QA_CHANNEL ? [process.env.QA_CHANNEL] : ['msedge', 'chrome', null];
  let lastErr;
  for (const channel of channels) {
    try {
      return await chromium.launch(channel ? { channel, headless: true } : { headless: true });
    } catch (err) {
      lastErr = err;
    }
  }
  throw new Error('No browser available. Run "npx playwright install chromium" or set QA_CHANNEL. ' + lastErr);
}

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const findings = [];
  const browser = await launch();
  const page = await browser.newPage({ viewport: { width: 1366, height: 900 } });
  const errors = [];
  page.on('console', m => { if (m.type() === 'error') errors.push('CONSOLE: ' + m.text()); });
  page.on('pageerror', e => errors.push('PAGEERROR: ' + e.message));

  await page.goto(FILE);
  await page.waitForTimeout(700);

  // 1. Navigation and console health
  const screens = [
    { key: 'dashboard', label: 'Dashboard' },
    { key: 'intake', label: 'Case Intake' },
    { key: 'radar', label: 'Overlap Radar' },
    { key: 'room', label: 'Coordination Rooms' },
    { key: 'institutions', label: 'Institutions' },
    { key: 'cases', label: 'All Cases' },
    { key: 'reports', label: 'Reports' },
    { key: 'audit', label: 'Audit Log' },
    { key: 'data', label: 'Data Layer' }
  ];
  for (const { key, label } of screens) {
    await page.evaluate(k => go(k), key);
    await page.waitForTimeout(250);
    const state = await page.evaluate(() => {
      const h = document.querySelector('.pagehead h1') || document.querySelector('#content h1');
      return { view: currentView, heading: h ? h.textContent : '(none)' };
    });
    console.log('NAV', label, '=> view=' + state.view, JSON.stringify(state.heading));
    if (state.view !== key) findings.push('Navigation to ' + label + ' did not change the view (currentView=' + state.view + ')');
    await page.screenshot({ path: path.join(OUT, label.replace(/\s+/g, '_') + '.png'), fullPage: true });
  }

  // 2. Intake -> resolve -> joint case
  await page.evaluate(() => go('intake'));
  await page.waitForTimeout(300);
  const load = page.getByRole('button', { name: /load sample/i });
  if (!(await load.count())) throw new Error('Load sample button not found');
  await load.first().click();
  await page.waitForTimeout(300);
  const resolve = page.getByRole('button', { name: /resolve/i });
  if (!(await resolve.count())) throw new Error('Resolve button not found');
  await resolve.first().click();
  await page.waitForTimeout(600);
  const body = await page.locator('body').innerText();
  console.log('INTAKE: open-case collision shown =', /open case/i.test(body));
  await page.screenshot({ path: path.join(OUT, 'intake_resolved.png'), fullPage: true });

  const joint = page.getByRole('button', { name: /create joint case/i });
  if (await joint.count()) {
    await joint.first().click();
    await page.waitForTimeout(700);
    console.log('JOINT: created, heading =', JSON.stringify(await page.evaluate(() => (document.querySelector('.pagehead h1') || {}).textContent || '(none)')));
    await page.screenshot({ path: path.join(OUT, 'joint_created.png'), fullPage: true });
  } else {
    findings.push('Joint case button not shown for the sample intake');
  }

  // 3. Audit verification + tamper probe
  await page.evaluate(() => go('audit'));
  await page.waitForTimeout(400);
  let verify = await page.$('#content button:has-text("Verify chain")');
  if (verify) { await verify.click(); await page.waitForTimeout(300); }
  const chainBefore = await page.textContent('#chainState');
  console.log('AUDIT: state =', JSON.stringify(chainBefore));

  const hashBefore = await page.evaluate(() => audit[0].hash);
  await page.evaluate(() => { audit[0].action = 'TAMPERED ACTION'; });
  await page.evaluate(() => go('audit'));
  await page.waitForTimeout(300);
  verify = await page.$('#content button:has-text("Verify chain")');
  if (verify) { await verify.click(); await page.waitForTimeout(300); }
  const chainAfter = await page.textContent('#chainState');
  const hashAfter = await page.evaluate(() => audit[0].hash);
  const tamperDetected = /broken|fail/i.test(chainAfter);
  console.log('TAMPER: hash changed =', hashBefore !== hashAfter, '| verifier =', JSON.stringify(chainAfter));
  if (!tamperDetected) {
    findings.push('P1-1 tamper not detected: a modified audit row is re-hashed and still reports intact');
  }

  // 4. Data Layer live label check
  await page.evaluate(() => { addAudit('QA probe action', 'C-2026-0198'); go('data'); });
  await page.waitForTimeout(300);
  const dataText = (await page.textContent('#content')).replace(/\s+/g, ' ');
  const idx = dataText.indexOf('Newest entry');
  const newestLabel = idx >= 0 ? dataText.slice(idx, idx + 30) : '(label not found)';
  const liveId = await page.evaluate(() => audit[0].id);
  console.log('DATA LAYER:', JSON.stringify(newestLabel), '| live id =', liveId);
  if (newestLabel.includes('A-1054') && liveId !== 'A-1054') {
    findings.push('P1-2 Data Layer label is stale after an action (shows A-1054, live is ' + liveId + ')');
  }

  // 5. Institution document hashes
  await page.evaluate(() => go('inst', 'i1'));
  await page.waitForTimeout(500);
  const hashes = await page.$$eval('.hash', els => els.map(e => e.textContent.trim()));
  const short = hashes.filter(h => /^[0-9a-f]{8}$/.test(h));
  console.log('DOC HASHES:', JSON.stringify(short));
  if (short.length && new Set(short).size < short.length) {
    findings.push('P1-3 institution documents repeat placeholder hashes: ' + JSON.stringify(short));
  }
  await page.screenshot({ path: path.join(OUT, 'institution_detail.png'), fullPage: true });

  // 6. Responsive overflow
  for (const w of [320, 360, 390, 768, 1024, 1366, 1920]) {
    await page.setViewportSize({ width: w, height: 900 });
    await page.waitForTimeout(150);
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
    console.log('WIDTH', w, 'overflow', overflow);
    if (overflow > 0) findings.push('Overflow ' + overflow + 'px at ' + w + 'px on institution detail');
  }

  // 7. Accessibility basics
  await page.setViewportSize({ width: 1366, height: 900 });
  const a11y = await page.evaluate(() => {
    const unnamedButtons = [...document.querySelectorAll('button')]
      .filter(b => !(b.innerText || '').trim() && !b.getAttribute('aria-label') && !b.getAttribute('title')).length;
    const missingAlt = [...document.querySelectorAll('img')].filter(i => !i.getAttribute('alt')).length;
    const unlabeledInputs = [...document.querySelectorAll('input,select,textarea')]
      .filter(el => !(el.id && document.querySelector(`label[for="${el.id}"]`)) && !el.getAttribute('aria-label') && !el.closest('label') && !el.getAttribute('placeholder')).length;
    return { unnamedButtons, missingAlt, unlabeledInputs };
  });
  console.log('A11Y', JSON.stringify(a11y));

  // 8. Summary
  console.log('CONSOLE ERRORS:', errors.length ? JSON.stringify(errors) : 'none');
  console.log('KNOWN FINDINGS:');
  if (!findings.length) console.log('  none in this run');
  for (const f of findings) console.log('  -', f);

  await browser.close();

  if (errors.length) process.exit(1);
  if (STRICT && findings.length) process.exit(1);
  process.exit(0);
})().catch(err => {
  console.error('QA FAILED:', err.message);
  process.exit(1);
});
