/**
 * CVPE Search — Pagefind client-side search
 * Pagefind index generated locally and committed to /public/pagefind/
 */

async function initSearch() {
  const input = document.getElementById('search-input');
  const results = document.getElementById('search-results');
  if (!input || !results) return;

  // Load Pagefind lazily on first interaction
  let pagefind;

  input.addEventListener('input', async () => {
    const query = input.value.trim();

    if (!pagefind && query.length > 1) {
      pagefind = await import('/pagefind/pagefind.js');
      await pagefind.init();
    }

    if (!pagefind || query.length < 2) {
      results.innerHTML = '';
      return;
    }

    const search = await pagefind.search(query);
    const data = await Promise.all(search.results.slice(0, 8).map(r => r.data()));

    if (data.length === 0) {
      results.innerHTML = '<p class="search-empty">No results.</p>';
      return;
    }

    results.innerHTML = data.map(r => `
      <a class="search-result" href="${r.url}">
        <span class="search-result-title">${r.meta.title}</span>
        <span class="search-result-excerpt">${r.excerpt}</span>
      </a>`).join('');
  });
}

document.addEventListener('DOMContentLoaded', initSearch);
