/* Browser-local enhancements; all core profile and paper content is static HTML. */
(() => {
  'use strict';
  const articles = [...document.querySelectorAll('.publication')];
  const groups = [...document.querySelectorAll('.year-group')];
  const filters = [...document.querySelectorAll('.filter')];
  const count = document.querySelector('#paper-count');
  const filterStatus = document.querySelector('#filter-status');

  function applyFilter(value, announce = true) {
    let visible = 0;
    articles.forEach(article => {
      const show = value === 'all' || article.dataset.category === value || (value === 'world' && article.dataset.world === 'true');
      article.hidden = !show;
      if (show) visible++;
    });
    groups.forEach(group => { group.hidden = !group.querySelector('.publication:not([hidden])'); });
    filters.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.filter === value)));
    count.textContent = visible;
    if (announce) filterStatus.textContent = `${visible} publication${visible === 1 ? '' : 's'} shown.`;
  }
  filters.forEach(button => button.addEventListener('click', () => applyFilter(button.dataset.filter)));

  // News anchors reveal their paper even when another topic is currently selected.
  function revealHashTarget() {
    if (location.hash.startsWith('#paper-')) {
      const article = document.getElementById(location.hash.slice(1));
      if (article && article.hidden) applyFilter('all', false);
      if (article) requestAnimationFrame(() => article.scrollIntoView({block:'start'}));
    }
  }
  window.addEventListener('hashchange', revealHashTarget);
  document.querySelectorAll('a[href^="#paper-"]').forEach(anchor => anchor.addEventListener('click', () => {
    const article = document.getElementById(anchor.hash.slice(1));
    if (article && article.hidden) applyFilter('all', false);
    if (article) requestAnimationFrame(() => article.scrollIntoView({block:'start'}));
  }));
  revealHashTarget();

  const nav = [...document.querySelectorAll('.side-nav a')];
  const sections = [...document.querySelectorAll('main > section')];
  function updateCurrentSection() {
    let current = sections[0];
    sections.forEach(section => { if (section.getBoundingClientRect().top <= 150) current = section; });
    if (window.innerHeight + window.scrollY >= document.documentElement.scrollHeight - 35) current = sections[sections.length - 1];
    nav.forEach(a => {
      if (a.hash === `#${current.id}`) a.setAttribute('aria-current', 'location');
      else a.removeAttribute('aria-current');
    });
  }
  let scheduled = false;
  window.addEventListener('scroll', () => {
    if (!scheduled) {
      scheduled = true;
      requestAnimationFrame(() => { updateCurrentSection(); scheduled = false; });
    }
  }, {passive:true});
  updateCurrentSection();

  const citationDialog = document.querySelector('#citation-dialog');
  const citationCode = document.querySelector('#citation-code');
  const copyStatus = document.querySelector('#copy-status');
  const imageDialog = document.querySelector('#image-dialog');
  let paperData;
  const loadPapers = () => paperData ||= fetch('publications.json').then(response => {
    if (!response.ok) throw new Error('Publication data unavailable');
    return response.json();
  }).then(papers => new Map(papers.map(paper => [paper.id, paper]))).catch(error => {paperData = undefined;throw error;});

  document.querySelectorAll('.bib-button').forEach(button => button.addEventListener('click', async () => {
    try {
      const paper = (await loadPapers()).get(button.dataset.paper);
      document.querySelector('#citation-title').textContent = paper.title;
      citationCode.textContent = paper.bibtex;
      const download = document.querySelector('#download-citation');
      download.href = `assets/citations/${paper.id}.bib`;
      download.download = `${paper.id}.bib`;
      copyStatus.textContent = '';
      citationDialog.showModal();
    } catch {
      // The static citation is still available if the JSON request fails.
      window.location.href = `assets/citations/${button.dataset.paper}.bib`;
    }
  }));

  document.querySelector('#copy-citation').addEventListener('click', async () => {
    try {
      await navigator.clipboard.writeText(citationCode.textContent);
      copyStatus.textContent = 'Copied to clipboard';
    } catch {
      const selection = window.getSelection();
      const range = document.createRange();
      range.selectNodeContents(citationCode);
      selection.removeAllRanges();
      selection.addRange(range);
      copyStatus.textContent = 'Citation selected. Use your copy shortcut.';
    }
  });

  document.querySelectorAll('[data-image]').forEach(anchor => anchor.addEventListener('click', event => {
    event.preventDefault();
    const article = anchor.closest('article');
    const preview = anchor.querySelector('img');
    const full = document.querySelector('#full-figure');
    document.querySelector('#image-heading').textContent = article.querySelector('.paper-title').textContent;
    full.src = preview.src;
    full.alt = preview.alt;
    imageDialog.showModal();
  }));

  document.querySelectorAll('dialog').forEach(dialog => {
    dialog.querySelector('[data-close]').addEventListener('click', () => dialog.close());
    dialog.addEventListener('click', event => {
      if (event.target === dialog) {
        const rect = dialog.getBoundingClientRect();
        if (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom) dialog.close();
      }
    });
  });
})();
