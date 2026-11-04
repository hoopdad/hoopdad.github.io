# hoopdad dunks

A Jekyll blog in `docs`, built on Chirpy with a custom editorial shell.

## Local development

With Ruby 3.1 or newer and Bundler installed:

```powershell
Set-Location docs
bundle install
bundle exec jekyll serve
```

On this workstation, Ruby is available through Ubuntu in WSL:

```powershell
wsl -d Ubuntu -- bash -lc 'cd /mnt/c/Users/mikeolivieri/source/hoopdad.github.io/docs; bundle3.2 exec jekyll build'
```

After building, `npm run preview` from `docs` serves `_site` at
`http://127.0.0.1:4173`. It is a local-only static preview, not a production server.

## Browser validation

From `docs`, run `npm ci`, `npx playwright install chromium`, and `npm test`.
Playwright starts and stops its own preview server. Tests cover desktop/mobile
discovery, search, series, theme persistence, code copy, original articles,
small-phone/tablet overflow, and navigation without JavaScript.

Set `BLOG_SCREENSHOTS` to an absolute directory to retain screenshots outside
the ignored `test-results` directory.

## Writing and discovery

- Keep posts in their existing topic `_posts` directories. Categories determine
  published URLs; changing them can break existing links.
- `topic` chooses the editorial section: `agents`, `ai-engineering`,
  `tokenomics`, `cloud`, or `data`. Defaults are in `docs\_config.yml`.
- `tags` can connect a post to other topics. Topic hubs and search include
  matching topic tags.
- `description` supplies a concise card and search summary.
- `series` and numeric `series_order` connect ordered chapters. Definitions and
  homepage entry points are in `docs\_data\series.yml` and `topics.yml`.
- `hidden: true` omits a post from discovery pages and the search index.

`docs\assets\editorial.scss` imports Chirpy's Sass foundation. The custom
layouts, local JavaScript, and assets replace the stock sidebar and scripts.
`docs\_plugins\editorial-assets.rb` prevents unused theme assets from competing
with the existing RSS feed, 404 page, and local search index.

## Publishing

The workflow in `.github\workflows\pages.yml` builds `docs` with Jekyll 4.
Pull requests build only; pushes to `main` also deploy to GitHub Pages.
Before publishing the theme migration, set the repository's **Settings > Pages >
Build and deployment > Source** to **GitHub Actions**. The legacy Pages builder
does not support this theme's dependency stack.
