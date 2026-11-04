(() => {
  'use strict';

  document.documentElement.classList.add('js-enabled');
  const themeToggle = document.querySelector('.theme-toggle');
  const updateThemeControl = () => {
    const dark = document.documentElement.dataset.bsTheme === 'dark';
    themeToggle.setAttribute('aria-label', `Switch to ${dark ? 'light' : 'dark'} mode`);
    document.querySelector('meta[name="theme-color"]').content = dark ? '#151c19' : '#f7f7f2';
  };
  if (themeToggle) {
    themeToggle.hidden = false;
    updateThemeControl();
    themeToggle.addEventListener('click', () => {
      const theme = document.documentElement.dataset.bsTheme === 'dark' ? 'light' : 'dark';
      document.documentElement.dataset.bsTheme = theme;
      try { localStorage.setItem('hoopdad-theme', theme); } catch (_) { /* Private browsing can disable storage. */ }
      updateThemeControl();
    });
  }

  const menuToggle = document.querySelector('.menu-toggle');
  const nav = document.querySelector('#primary-nav');
  const setMenu = (open) => {
    nav.classList.toggle('is-open', open);
    menuToggle.setAttribute('aria-expanded', String(open));
    menuToggle.querySelector('span').textContent = open ? '-' : '+';
  };
  if (menuToggle && nav) {
    menuToggle.hidden = false;
    menuToggle.addEventListener('click', () => setMenu(menuToggle.getAttribute('aria-expanded') !== 'true'));
  }
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') {
      const dropdown = document.querySelector('.more-topics[open]');
      if (dropdown) {
        dropdown.open = false;
        dropdown.querySelector('summary').focus();
      } else if (menuToggle && menuToggle.getAttribute('aria-expanded') === 'true') {
        setMenu(false);
        menuToggle.focus();
      }
    }
    if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'k') {
      event.preventDefault();
      const input = document.querySelector('#search-input');
      if (input) input.focus();
      else window.location.assign(document.querySelector('.search-link').href);
    }
  });
  document.addEventListener('click', (event) => {
    const dropdown = document.querySelector('.more-topics[open]');
    if (dropdown && !dropdown.contains(event.target)) dropdown.open = false;
  });

  const article = document.querySelector('#article-content');
  if (article) {
    const headings = [...article.querySelectorAll('h2, h3')];
    const toc = document.querySelector('#article-toc');
    if (toc && headings.length) {
      const links = new Map();
      headings.forEach((heading, index) => {
        if (!heading.id) heading.id = `section-${index + 1}`;
        const link = document.createElement('a');
        link.href = `#${encodeURIComponent(heading.id)}`;
        link.textContent = heading.textContent;
        if (heading.tagName === 'H3') link.className = 'toc-subheading';
        toc.append(link);
        links.set(heading, link);
      });
      document.querySelector('.reading-toc').hidden = false;
      if (matchMedia('(max-width: 1000px)').matches) document.querySelector('.reading-toc details').open = false;
      const observer = new IntersectionObserver((entries) => {
        const current = entries.find((entry) => entry.isIntersecting);
        if (!current) return;
        toc.querySelectorAll('[aria-current]').forEach((link) => link.removeAttribute('aria-current'));
        links.get(current.target).setAttribute('aria-current', 'location');
      }, { rootMargin: '-100px 0px -55% 0px' });
      headings.forEach((heading) => observer.observe(heading));
    }
    article.querySelectorAll('table').forEach((table) => {
      const wrapper = document.createElement('div');
      wrapper.className = 'table-scroll';
      wrapper.tabIndex = 0;
      wrapper.setAttribute('role', 'region');
      wrapper.setAttribute('aria-label', 'Scrollable article table');
      table.before(wrapper);
      wrapper.append(table);
    });
    article.querySelectorAll('pre').forEach((pre) => {
      pre.tabIndex = 0;
      pre.setAttribute('aria-label', 'Code example');
      if (!navigator.clipboard) return;
      const wrapper = document.createElement('div');
      wrapper.className = 'code-container';
      const button = document.createElement('button');
      button.type = 'button';
      button.className = 'copy-code';
      button.textContent = 'Copy code';
      button.setAttribute('aria-label', 'Copy code example');
      button.setAttribute('aria-live', 'polite');
      pre.before(wrapper);
      wrapper.append(button, pre);
      button.addEventListener('click', async () => {
        try {
          await navigator.clipboard.writeText(pre.querySelector('code')?.textContent || pre.textContent);
          button.textContent = 'Copied';
        } catch (_) {
          button.textContent = 'Select to copy';
          const range = document.createRange();
          range.selectNodeContents(pre);
          const selection = window.getSelection();
          selection.removeAllRanges();
          selection.addRange(range);
        }
        setTimeout(() => { button.textContent = 'Copy code'; }, 2000);
      });
    });
  }

  const form = document.querySelector('.search-form');
  if (!form) return;
  const input = document.querySelector('#search-input');
  const topic = document.querySelector('#search-topic');
  const status = document.querySelector('#search-status');
  const results = document.querySelector('#search-results');
  const params = new URLSearchParams(window.location.search);
  input.value = params.get('q') || '';
  topic.value = params.get('topic') || '';
  const normalize = (text) => text.toLowerCase().replace(/[-_]/g, ' ').replace(/\s+/g, ' ').trim();
  let indexPromise;
  let revision = 0;
  let debounce;
  const loadIndex = () => {
    if (!indexPromise) {
      indexPromise = fetch(form.dataset.index).then((response) => {
        if (!response.ok) throw new Error('Search index unavailable');
        return response.json();
      }).catch((error) => { indexPromise = undefined; throw error; });
    }
    return indexPromise;
  };
  const createResult = (post) => {
    const card = document.createElement('article');
    card.className = 'article-card';
    const metadata = document.createElement('div');
    metadata.className = 'card-meta';
    const topicLink = document.createElement('a');
    topicLink.className = 'topic-label';
    topicLink.href = post.topicUrl;
    topicLink.textContent = post.topicTitle;
    metadata.append(topicLink);
    const title = document.createElement('h3');
    const link = document.createElement('a');
    link.href = post.url;
    link.textContent = post.title;
    title.append(link);
    const description = document.createElement('p');
    description.textContent = post.description;
    const footer = document.createElement('div');
    footer.className = 'card-footer';
    const date = document.createElement('span');
    date.textContent = post.date;
    const read = document.createElement('a');
    read.href = post.url;
    read.textContent = 'Read essay \u2192';
    read.setAttribute('aria-label', `Read ${post.title}`);
    footer.append(date, read);
    card.append(metadata, title, description, footer);
    return card;
  };
  const search = async () => {
    const currentRevision = ++revision;
    const query = input.value.trim();
    const selectedTopic = topic.value;
    const url = new URL(window.location.href);
    if (query) url.searchParams.set('q', query); else url.searchParams.delete('q');
    if (selectedTopic) url.searchParams.set('topic', selectedTopic); else url.searchParams.delete('topic');
    history.replaceState(null, '', url);
    results.replaceChildren();
    if (!query && !selectedTopic) {
      status.textContent = 'Enter a phrase or choose a topic to explore the archive.';
      return;
    }
    status.textContent = 'Searching the field notes...';
    try {
      const posts = await loadIndex();
      if (currentRevision !== revision) return;
      const terms = normalize(query).split(' ').filter(Boolean);
      const matches = posts.filter((post) => !selectedTopic || post.topic === selectedTopic || post.tags.includes(selectedTopic))
        .map((post) => {
          const title = normalize(post.title);
          const metadata = normalize(`${post.topicTitle} ${post.topic} ${post.tags.join(' ')} ${post.description}`);
          const body = normalize(post.content);
          const score = terms.every((term) => title.includes(term) || metadata.includes(term) || body.includes(term))
            ? terms.reduce((total, term) => total + (title.includes(term) ? 5 : metadata.includes(term) ? 2 : 1), 0)
            : -1;
          return { post, score };
        }).filter((match) => match.score >= 0).sort((a, b) => b.score - a.score);
      status.textContent = matches.length ? `${matches.length} ${matches.length === 1 ? 'article' : 'articles'} found${query ? ` for "${query}"` : ''}.` : 'No articles found. Try fewer words or choose another topic.';
      results.replaceChildren(...matches.map(({ post }) => createResult(post)));
    } catch (_) {
      if (currentRevision === revision) status.textContent = 'Search could not load. Try again, or browse All writing in the footer.';
    }
  };
  form.addEventListener('submit', (event) => {
    event.preventDefault();
    clearTimeout(debounce);
    search();
  });
  input.addEventListener('input', () => {
    ++revision;
    clearTimeout(debounce);
    debounce = setTimeout(search, 150);
  });
  topic.addEventListener('change', () => {
    clearTimeout(debounce);
    search();
  });
  if (input.value || topic.value) search();
})();
