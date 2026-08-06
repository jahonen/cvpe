/**
 * CVPE Subscribe — via Cloudflare Worker proxy
 *
 * The SendGrid API key lives server-side in the Worker
 * (workers/subscribe/worker.js, deployed at api.cvpe.eu).
 * No secrets ship with this static site.
 */

const SUBSCRIBE_ENDPOINT = 'https://api.cvpe.eu/subscribe';

async function handleSubscribe(event) {
  event.preventDefault();
  const form = event.target;
  const email = form.querySelector('input[type="email"]').value.trim();
  const btn = form.querySelector('button[type="submit"]');
  const msg = form.querySelector('.subscribe-message');

  if (!email) return;

  btn.disabled = true;
  btn.textContent = 'Subscribing...';

  try {
    const res = await fetch(SUBSCRIBE_ENDPOINT, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email })
    });

    if (res.ok) {
      msg.textContent = 'Subscribed. Essays delivered to your inbox.';
      msg.className = 'subscribe-message subscribe-message--success';
      form.querySelector('input[type="email"]').value = '';
    } else {
      throw new Error('Subscribe failed');
    }
  } catch {
    msg.textContent = 'Something went wrong. Try again, or subscribe via RSS: cvpe.eu/feed.xml';
    msg.className = 'subscribe-message subscribe-message--error';
  } finally {
    btn.disabled = false;
    btn.textContent = 'Subscribe';
  }
}

document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('subscribe-form');
  if (form) form.addEventListener('submit', handleSubscribe);
});
