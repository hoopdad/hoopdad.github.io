const { test, expect } = require('@playwright/test');
const fs = require('node:fs/promises');
const path = require('node:path');
const { createHash } = require('node:crypto');

const topicKeys = ['agents', 'ai-engineering', 'tokenomics', 'cloud', 'data'];
const screenshot = async (page, testInfo, name, fullPage = false) => {
  const directory = process.env.BLOG_SCREENSHOTS || testInfo.outputDir;
  await fs.mkdir(directory, { recursive: true });
  await page.screenshot({ path: path.join(directory, `${testInfo.project.name}-${name}.png`), fullPage });
};
const noOverflow = async (page) => {
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth + 1)).toBe(true);
};
const openNavigation = async (page) => {
  const menu = page.getByRole('button', { name: 'Menu' });
  if (await menu.isVisible()) await menu.click();
};

test('curated home, topic hierarchy, and accessible navigation', async ({ page }, testInfo) => {
  const errors = [];
  page.on('pageerror', (error) => errors.push(error.message));
  await page.goto('/');
  await expect(page.getByRole('heading', { level: 1 })).toContainText('Building agents');
  await expect(page.locator('.topic-card')).toHaveCount(3);
  await expect(page.locator('.series-card')).toHaveCount(3);
  await expect(page.locator('.article-card')).toHaveCount(6);
  await expect(page.locator('.foundations')).toContainText('Cloud Architecture');
  await expect(page.locator('.foundations')).toContainText('Data Engineering');
  await page.evaluate(() => document.fonts.ready);
  await noOverflow(page);
  await screenshot(page, testInfo, 'home', true);
  await screenshot(page, testInfo, 'home-top');
  await openNavigation(page);
  const nav = page.getByRole('navigation', { name: 'Primary', exact: true });
  await nav.getByRole('link', { name: 'Agents', exact: true }).click();
  await expect(page).toHaveURL(/\/topics\/agents\/$/);
  await expect(page.locator('.article-grid')).toContainText('Continuous Learning with Agent Communication Skills');
  await expect(page.locator('.article-grid')).toContainText('Token Efficiency Lessons From Loop Engineering Part 4');
  await screenshot(page, testInfo, 'agents');
  await openNavigation(page);
  await page.locator('.more-topics summary').click();
  await page.getByRole('link', { name: 'Cloud Architecture', exact: true }).first().click();
  await expect(page).toHaveURL(/\/topics\/cloud\/$/);
  await expect(page.locator('.article-card')).toHaveCount(6);
  await noOverflow(page);
  expect(errors).toEqual([]);
});

test('full-text search, topic filters, empty results, and deep links', async ({ page }, testInfo) => {
  await page.goto('/search/?q=loop%20engineering');
  await expect(page.locator('#search-status')).toContainText('articles found');
  await expect(page.locator('#search-results')).toContainText('Token Efficiency Lessons From Loop Engineering Part 1');
  await page.locator('#search-input').fill('private');
  await page.locator('#search-topic').selectOption('cloud');
  await expect(page.locator('#search-status')).toContainText('found');
  await expect(page.locator('#search-results .article-card')).not.toHaveCount(0);
  await expect(page.locator('#search-results .topic-label').first()).toHaveText('Cloud Architecture');
  await screenshot(page, testInfo, 'search');
  await page.locator('#search-input').fill('zzzznoarticle');
  await expect(page.locator('#search-status')).toContainText('No articles found');
  await expect(page.locator('#search-results .article-card')).toHaveCount(0);
  await page.locator('#search-input').fill('');
  await page.locator('#search-topic').selectOption('data');
  await expect(page.locator('#search-results .article-card')).toHaveCount(4);
  await page.reload();
  await expect(page.locator('#search-results .article-card')).toHaveCount(4);
  await noOverflow(page);
});

test('ordered series, reading navigation, table of contents, and feedback', async ({ page }, testInfo) => {
  await page.goto('/series/token-efficiency/');
  await expect(page.locator('.chapter-list li')).toHaveCount(3);
  await page.getByRole('link', { name: 'Start with part one' }).click();
  await expect(page).toHaveURL(/\/tokenomics\/2026\/05\/27\/token-efficiency-part1\.html$/);
  await expect(page.locator('.series-banner')).toContainText('Part 1 of 3');
  await expect(page.locator('.reading-toc')).toBeVisible();
  if (testInfo.project.name === 'mobile') await page.locator('.reading-toc summary').click();
  await expect(page.locator('#article-toc a').first()).toBeVisible();
  await screenshot(page, testInfo, 'article');
  await page.locator('#article-toc a').first().click();
  await expect(page).toHaveURL(/\.html#/);
  await screenshot(page, testInfo, 'article-reading');
  await expect(page.locator('.post-feedback a[href*="discussions/new"]')).toHaveCount(3);
  await page.getByRole('navigation', { name: 'Series chapters' }).getByRole('link', { name: 'Next chapter' }).click();
  await expect(page.locator('.series-banner')).toContainText('Part 2 of 3');
  await expect(page.getByRole('navigation', { name: 'Series chapters' }).getByRole('link', { name: 'Previous chapter' })).toBeVisible();
  await noOverflow(page);
});

test('theme preference persists between pages and keyboard menu closes', async ({ page }, testInfo) => {
  await page.goto('/');
  await page.getByRole('button', { name: 'Switch to dark mode' }).click();
  await expect(page.locator('html')).toHaveAttribute('data-bs-theme', 'dark');
  await screenshot(page, testInfo, 'dark-home');
  await page.goto('/archive/');
  await expect(page.locator('html')).toHaveAttribute('data-bs-theme', 'dark');
  await expect(page.locator('.archive-row')).toHaveCount(35);
  await noOverflow(page);
  await page.getByRole('button', { name: 'Switch to light mode' }).click();
  await expect(page.locator('html')).toHaveAttribute('data-bs-theme', 'light');
  await openNavigation(page);
  await page.locator('.more-topics summary').click();
  await page.keyboard.press('Escape');
  await expect(page.locator('.more-topics')).not.toHaveAttribute('open', '');
  if (testInfo.project.name === 'mobile') {
    await page.keyboard.press('Escape');
    await expect(page.getByRole('button', { name: 'Menu' })).toHaveAttribute('aria-expanded', 'false');
  }
});

test('all original articles, topic hubs, internal discovery links, and feed resolve', async ({ page, request }) => {
  const indexResponse = await request.get('/search.json');
  expect(indexResponse.ok()).toBe(true);
  const posts = await indexResponse.json();
  expect(posts).toHaveLength(35);
  for (const post of posts) {
    expect(topicKeys).toContain(post.topic);
    const response = await request.get(post.url);
    expect(response.ok(), post.url).toBe(true);
    expect(await response.text(), post.url).toContain('class="reading-page"');
    await page.goto(post.url);
    await noOverflow(page);
  }
  for (const topic of topicKeys) {
    await page.goto(`/topics/${topic}/`);
    await expect(page.locator('.topic-page h1')).toBeVisible();
    await expect(page.locator('.article-card').first()).toBeVisible();
    await noOverflow(page);
  }
  for (const route of ['/', '/series/', '/archive/', '/about/']) {
    await page.goto(route);
    const links = await page.locator('main a[href^="/"]').evaluateAll((nodes) => [...new Set(nodes.map((node) => node.getAttribute('href').split('#')[0]))]);
    for (const link of links) expect((await request.get(link)).ok(), link).toBe(true);
  }
  const feed = await request.get('/feed.xml');
  expect(feed.ok()).toBe(true);
  const feedText = await feed.text();
  expect(feedText).toContain('http://www.w3.org/2005/Atom');
  expect(feedText).toContain(posts[0].url);
  await page.goto('/missing-page');
  await expect(page.getByRole('heading', { level: 1 })).toHaveText('This page took a different path.');
});

test('code copy works and long code stays inside the reading column', async ({ page, context }, testInfo) => {
  await context.grantPermissions(['clipboard-read', 'clipboard-write']);
  await page.goto('/ai/2026/04/01/foundry-hosted-agents-v2-with-mcp-tools.html');
  const pre = page.locator('.prose pre').first();
  await expect(pre).toBeVisible();
  const expected = await pre.locator('code').textContent();
  await page.getByRole('button', { name: 'Copy code example' }).first().click();
  await expect(page.getByRole('button', { name: 'Copy code example' }).first()).toHaveText('Copied');
  const copied = await page.evaluate(() => navigator.clipboard.readText());
  expect(copied.replace(/\r\n/g, '\n')).toBe(expected);
  await pre.scrollIntoViewIfNeeded();
  await screenshot(page, testInfo, 'code');
  await noOverflow(page);
});

test('small phones and tablet layouts do not overflow', async ({ page }) => {
  for (const width of [320, 768, 1024]) {
    await page.setViewportSize({ width, height: 900 });
    for (const route of ['/', '/archive/', '/search/', '/topics/agents/']) {
      await page.goto(route);
      await noOverflow(page);
    }
  }
});

test('navigation and reading remain available without JavaScript', async ({ browser }, testInfo) => {
  const context = await browser.newContext({
    javaScriptEnabled: false,
    viewport: testInfo.project.use.viewport,
    baseURL: 'http://127.0.0.1:4173'
  });
  const page = await context.newPage();
  await page.goto('/');
  const nav = page.getByRole('navigation', { name: 'Primary', exact: true });
  await expect(nav.getByRole('link', { name: 'Agents', exact: true })).toBeVisible();
  await nav.getByRole('link', { name: 'Agents', exact: true }).click();
  await expect(page.locator('.topic-page h1')).toHaveText('Agents');
  await page.goto('/search/');
  await page.getByRole('link', { name: 'browse every article in the archive' }).click();
  await expect(page.locator('.archive-row')).toHaveCount(35);
  await noOverflow(page);
  await context.close();
});

test('claims reference assets are local, intact, and browsable', async ({ page, request }) => {
  const assetBase = '/assets/2026/tokenomics/think-fast-tests/';
  await page.goto('/tokenomics/2026/11/03/maximize-ai-insurance-workflow1.html');
  await expect(page.locator('.prose a[href*="github.com/hoopdad/think-fast-tests"]')).toHaveCount(0);
  const references = await page.locator(`.prose a[href^="${assetBase}"]`).evaluateAll(
    (nodes) => [...new Set(nodes.map((node) => node.getAttribute('href')))]
  );
  expect(references).toContain(`${assetBase}bundle-manifest.json`);
  const manifestResponse = await request.get(`${assetBase}bundle-manifest.json`);
  expect(manifestResponse.ok()).toBe(true);
  const manifest = await manifestResponse.json();
  const available = new Set([`${assetBase}bundle-manifest.json`]);
  for (const file of manifest.files) {
    const url = `${assetBase}${file.path}`;
    available.add(url);
    const response = await request.get(url);
    expect(response.ok(), url).toBe(true);
    const hash = createHash('sha256').update(await response.body()).digest('hex');
    expect(hash, url).toBe(file.served_sha256);
  }
  for (const reference of references) expect(available.has(reference), reference).toBe(true);
  for (const file of manifest.files.filter((file) => file.path.endsWith('.html'))) {
    await page.goto(`${assetBase}${file.path}`);
    await expect(page.locator('h1')).toBeVisible();
    const links = await page.locator('a[href]').evaluateAll((nodes) =>
      nodes.map((node) => new URL(node.getAttribute('href'), location.href))
        .filter((url) => url.origin === location.origin)
        .map((url) => url.pathname)
    );
    for (const link of links) expect(available.has(link), link).toBe(true);
  }
  await page.goto(`${assetBase}assets/runs/analysis-h2-r6-wus3-20261029-v2/index.html`);
  await expect(page.locator('svg').first()).toBeVisible();
  await page.locator('a[href="evaluation.html"]').first().click();
  await expect(page).toHaveURL(/\/evaluation\.html$/);
  await expect(page.locator('#repeatability')).toBeVisible();
});
