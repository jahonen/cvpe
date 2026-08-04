/**
 * CVPE Subscribe — SendGrid integration
 * Single email field, plain POST to SendGrid Contacts API
 *
 * NOTE: SENDGRID_API_KEY must be injected at build time or, preferably,
 * the request proxied through a lightweight serverless endpoint
 * (DanubeData edge function / PHP endpoint) to avoid exposing the key
 * client-side in production. Leave empty until configured.
 */

const SENDGRID_API_KEY = '';

async function handleSubscribe(event) {
  event.preventDefault();
  const form = event.target;
  const email = form.querySelector('input[type="email"]').value.trim();
  const btn = form.querySelector('button[type="submit"]');
  const msg = form.querySelector('.subscribe-message');

  if (!email) return;

  if (!SENDGRID_API_KEY) {
    msg.textContent = 'Subscriptions open shortly. Meanwhile, follow on Bluesky or subscribe via RSS: cvpe.eu/feed.xml';
    msg.className = 'subscribe-message subscribe-message--error';
    return;
  }

  btn.disabled = true;
  btn.textContent = 'Subscribing...';

  try {
    const res = await fetch('https://api.sendgrid.com/v3/marketing/contacts', {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${SENDGRID_API_KEY}`
      },
      body: JSON.stringify({
        contacts: [{ email }]
      })
    });

    if (res.ok) {
      msg.textContent = 'Subscribed. Essays delivered to your inbox.';
      msg.className = 'subscribe-message subscribe-message--success';
      form.querySelector('input[type="email"]').value = '';
    } else {
      throw new Error('SendGrid error');
    }
  } catch {
    msg.textContent = 'Something went wrong. Try again or email directly.';
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
