/**
 * CVPE Bluesky Integration
 * Fetches thread replies from AT Protocol public API
 * No authentication required — public posts only
 */

const BSKY_API = 'https://public.api.bsky.app/xrpc';

async function loadBlueskyThread(threadUri, containerId) {
  const container = document.getElementById(containerId);
  if (!container) return;

  if (!threadUri) {
    container.innerHTML = `
      <p class="bsky-empty">
        Discussion thread opens on Bluesky when this essay is posted.
        <a href="https://bsky.app/profile/jpahonen.eurosky.social"
           target="_blank" rel="noopener">
          Follow @jpahonen.eurosky.social →
        </a>
      </p>`;
    return;
  }

  container.innerHTML = '<p class="bsky-loading">Loading discussion...</p>';

  try {
    const encoded = encodeURIComponent(threadUri);
    const res = await fetch(
      `${BSKY_API}/app.bsky.feed.getPostThread?uri=${encoded}&depth=50`
    );
    if (!res.ok) throw new Error('Thread fetch failed');

    const data = await res.json();
    const replies = data.thread?.replies || [];

    if (replies.length === 0) {
      container.innerHTML = `
        <p class="bsky-empty">
          No replies yet.
          <a href="https://bsky.app/profile/jpahonen.eurosky.social"
             target="_blank" rel="noopener">
            Join the conversation on Bluesky →
          </a>
        </p>`;
      return;
    }

    const html = replies
      .filter(r => r.post)
      .sort((a, b) => new Date(a.post.indexedAt) - new Date(b.post.indexedAt))
      .map(r => {
        const post = r.post;
        const author = post.author;
        const date = new Date(post.indexedAt).toLocaleDateString('en-GB', {
          day: 'numeric', month: 'short', year: 'numeric'
        });
        const postUrl = `https://bsky.app/profile/${author.handle}/post/${post.uri.split('/').pop()}`;
        return `
          <div class="bsky-reply">
            <div class="bsky-reply-header">
              <strong class="bsky-author">${escapeHtml(author.displayName || author.handle)}</strong>
              <span class="bsky-handle">@${escapeHtml(author.handle)}</span>
              <time class="bsky-date" datetime="${post.indexedAt}">${date}</time>
            </div>
            <p class="bsky-text">${escapeHtml(post.record.text)}</p>
            <a class="bsky-link" href="${postUrl}" target="_blank" rel="noopener">
              View on Bluesky ↗
            </a>
          </div>`;
      }).join('');

    container.innerHTML = `
      <div class="bsky-thread">${html}</div>
      <a class="bsky-cta"
         href="https://bsky.app/profile/jpahonen.eurosky.social"
         target="_blank" rel="noopener">
        Reply on Bluesky →
      </a>`;
  } catch (err) {
    container.innerHTML = `
      <p class="bsky-error">
        Discussion unavailable.
        <a href="https://bsky.app/profile/jpahonen.eurosky.social"
           target="_blank" rel="noopener">
          Find the thread on Bluesky →
        </a>
      </p>`;
  }
}

function escapeHtml(str) {
  const div = document.createElement('div');
  div.appendChild(document.createTextNode(str));
  return div.innerHTML;
}

async function loadRecentPosts(handle, containerId, count = 3) {
  const container = document.getElementById(containerId);
  if (!container) return;

  try {
    const res = await fetch(
      `${BSKY_API}/app.bsky.feed.getAuthorFeed?actor=${handle}&limit=${count}`
    );
    if (!res.ok) throw new Error('Feed fetch failed');

    const data = await res.json();
    const posts = data.feed?.slice(0, count) || [];

    const html = posts.map(item => {
      const post = item.post;
      const date = new Date(post.indexedAt).toLocaleDateString('en-GB', {
        day: 'numeric', month: 'short', year: 'numeric'
      });
      const likes = post.likeCount || 0;
      const url = `https://bsky.app/profile/${post.author.handle}/post/${post.uri.split('/').pop()}`;
      return `
        <div class="bsky-post">
          <p class="bsky-post-text">${escapeHtml(post.record.text)}</p>
          <p class="bsky-post-meta">
            <time datetime="${post.indexedAt}">${date}</time>
            ${likes > 0 ? `· ${likes.toLocaleString()} likes` : ''}
            · <a href="${url}" target="_blank" rel="noopener">View →</a>
          </p>
        </div>`;
    }).join('');

    container.innerHTML = html;
  } catch (err) {
    container.innerHTML = '';
  }
}
