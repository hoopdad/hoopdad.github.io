# Repository index

## Freshness
- Baseline: `211a900` (`publishing first decision model post`).
- Considered the Chirpy migration, custom layouts/assets, topic and series pages,
  content metadata, local browser tooling, README, and Pages workflow.
- Added topic/series data and hubs, archive/search, layout/card overrides, the
  asset-filter plugin, locked dependencies, and browser tests. Replaced
  `docs\assets\main.scss` with `editorial.scss`. Article illustrations also live
  under `docs\assets\2026\tokenomics`; draft content may be concurrent user work.
- Added claims screenshots 3, 4, 5, and 7 under that asset directory and linked
  them   from the published insurance-workflow post. Its measured results/source examples
  are filled; quality uses separately labeled evaluator post-hoc majorities.
- Copied its referenced implementation/report snapshots and linked report
  dependencies into `docs\assets\2026\tokenomics\think-fast-tests`. Relative
  folders preserve report navigation; `bundle-manifest.json` records source/
  hosted hashes and replacements for three missing private-runtime links.
  Its scoped `.gitattributes` preserves bytes across checkouts for those hashes.

## Functional areas
- `docs` is the Jekyll site source, using Chirpy's Sass with a custom editorial shell.
- Content lives in `docs\ai\_posts`, `docs\tokenomics\_posts`, `docs\cloud\_posts`, and `docs\data\_posts`. Cloud and tokenomics also have `_drafts`.
- `docs\assets\editorial.scss` owns responsive light/dark styling; `site.js` owns
  menu/theme, local search, article contents, table scrolling, and code copy.
- `docs\_data\topics.yml` and `series.yml` define primary Agents/AI Engineering/
  Tokenomics discovery and secondary Cloud/Data foundations.
- `docs\topics`, `docs\series`, `archive.html`, and `search.html` provide browsing.
- `docs\about.md` supplies the About page.

## Technical layers and boundaries
- `docs\_config.yml` defines identity, explicit URL-preserving permalinks, topic
  defaults, Chirpy, SEO, sitemap, and feed.
- `docs\index.md` selects `_layouts\home.html`: curated topics, ordered series,
  latest writing, then foundations. Discovery omits `hidden` posts.
- `_layouts\default.html` supplies the custom shell and production-only analytics;
  `header.html` supplies navigation. `post.html` adds reading/series navigation,
  related writing, contents, and the existing feedback include.
- `topic.html`/`series.html` and `post-card.html`/`series-card.html` share metadata-driven discovery.
- `docs\search.json` exports public posts to `site.js`; search stays browser-local.
- `docs\_plugins\editorial-assets.rb` removes unused theme-origin pages/static assets
  to prevent feed/404/search conflicts, while retaining Chirpy Sass.
- `docs\Gemfile` and tracked `Gemfile.lock` manage Ruby dependencies.
- `docs\_site` and `docs\vendor` are generated output and installed dependencies, not authoring targets.

## Navigation
- Homepage discovery and topic hierarchy: `docs\_layouts\home.html`, `_data\topics.yml`,
  `docs\topics`, and post `topic`/`tags` metadata.
- Reading series: `_data\series.yml`, `docs\series`, and post `series`/`series_order`.
- Visual design: `docs\assets\editorial.scss`, layouts, and header include.
- Branding and navigation: `docs\_config.yml`, `docs\_includes\header.html`, `docs\about.md`.
- Article reading experience: `docs\_layouts\post.html`, `editorial.scss`, `site.js`, feedback include.
- Search: `search.html`, `search.json`, and `site.js`.
- Claims article evidence/source downloads: `docs\assets\2026\tokenomics\think-fast-tests`;
  copied static snapshots, not an executable package or private runtime export.
- Build/deployment: README, Gemfile/lockfile, `_config.yml`, plugin, `.github\workflows\pages.yml`.

## Conventions and validation
- Posts use dated Markdown filenames and YAML front matter with `layout: post` and `title`; representative recent posts omit explicit categories.
- Topic directory names participate in Jekyll post categorization and existing URLs; preserve article URLs during redesign.
- `topic` is separate from URL categories; `tags` cross-list topics. Optional
  `description` supplies card/search copy, and numeric `series_order` orders chapters.
- Run Jekyll commands from `docs`: `bundle exec jekyll build`.
- `drafts-view.ps1` and `drafts-view.sh` serve drafts with `bundle exec jekyll serve -D`; the PowerShell helper configures local gems and restores missing dependencies.
- Browser checks from `docs`: `npm test`. `playwright.config.cjs` owns desktop/mobile
  projects and a temporary loopback preview; `tests\blog.spec.cjs` covers discovery,
  search, articles, series, theme, copy, responsive overflow, and no-JS navigation.
- `BLOG_SCREENSHOTS` retains screenshots outside ignored test output. `_site`,
  vendor, node_modules, and test-results are generated, not authoring targets.
- The Pages workflow builds PRs and deploys main; remote Pages must use GitHub
  Actions rather than the legacy `/docs` builder before publishing the migration.
