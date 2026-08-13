/**
 * CVPE Alignment Discovery Tool
 *
 * 14 statements, two per star. Four options scoring 0-3. Each star lands on a
 * raw 0-6, banded into not-aligned / mixed / aligned. There is deliberately no
 * single overall score: the point is the shape across the seven, not a verdict.
 *
 * No cookies, no storage, no backend. A result is seven digits in the URL
 * (?r=6463253) and nothing else — sharing a link is the entire mechanism.
 */

const STARS = [
  { slug: 'ownership',           name: 'Ownership and Control',                 short: 'Ownership' },
  { slug: 'earned-trust',        name: 'Institutional Trust, Earned',           short: 'Trust' },
  { slug: 'belonging',           name: 'Civic Belonging as Practice',           short: 'Belonging' },
  { slug: 'proximity-politics',  name: 'Proximity Politics',                    short: 'Proximity' },
  { slug: 'natural-monopolies',  name: 'Public Ownership of Natural Monopolies', short: 'Commons' },
  { slug: 'new-commenda',        name: 'A Fair Deal Between Public and Private', short: 'Commenda' },
  { slug: 'tapestry',            name: 'One Pattern, Many Threads',             short: 'Tapestry' }
];

/* Fixed order, interleaved so a star's two statements never sit back to back. */
const QUESTIONS = [
  { star: 0, text: 'A company should only be called European if Europeans actually control what happens to it, even if that means turning down foreign investment.' },
  { star: 1, text: 'Institutions, including the EU itself, should have to keep earning public trust, not receive it automatically because they’ve existed a long time.' },
  { star: 2, text: 'Belonging to a country or to Europe should be built through participation and effort, not just granted by birth.' },
  { star: 3, text: 'Decisions should usually be made by the people closest to the consequences, not by a distant central authority, unless there’s a strong reason otherwise.' },
  { star: 4, text: 'Power grids, rail networks, and core data infrastructure work better in public hands, because there’s no real competition possible for them anyway.' },
  { star: 5, text: 'When public money helps fund a major private risk, like advanced technology, the public deserves a permanent stake in the outcome, not just a one-time grant.' },
  { star: 6, text: 'Europe needs a genuinely unified defence force with its own budget and command, not twenty-seven separate small ones.' },
  { star: 0, text: 'Registering a business in Europe, or putting a flag on something, shouldn’t be enough on its own to call it sovereign.' },
  { star: 1, text: 'When an institution fails the public, it’s better to say so plainly than to defend it out of loyalty.' },
  { star: 2, text: 'Someone who wasn’t born here but contributes actively can belong just as much as someone who was.' },
  { star: 3, text: 'This applies beyond borders — energy, infrastructure, and culture should mostly be decided locally too, escalating upward only when it’s genuinely necessary.' },
  { star: 4, text: 'Private companies can still build and innovate on top of publicly owned infrastructure — public ownership of the foundation isn’t the same as banning private involvement.' },
  { star: 5, text: 'Some European technology, like a future European AI model, is important enough that public ownership should never be allowed to drop low enough for foreign control to take over.' },
  { star: 6, text: 'That unified force should still preserve each nation’s own military identity and traditions, rather than blending everyone into one uniform look.' }
];

const OPTIONS = [
  { label: 'Strongly disagree', value: 0 },
  { label: 'Disagree',          value: 1 },
  { label: 'Agree',             value: 2 },
  { label: 'Strongly agree',    value: 3 }
];

/* Per-star readout for each band. Written to describe, never to grade. */
const READOUTS = [
  { low: 'You are not persuaded that ownership is the right test of what counts as European. That is a real disagreement with this star, and worth reading the argument behind it.',
    mid: 'You accept part of the ownership test, probably with conditions about when foreign investment is worth the trade-off.',
    high:'You think sovereignty means actually owning and controlling a thing. That is exactly what this star argues.' },
  { low: 'You are more willing than this star to extend institutions the benefit of the doubt, or you read public criticism of them as corrosive rather than healthy.',
    mid: 'You expect institutions to earn trust, but you are more cautious than this star about saying so publicly when they fail.',
    high:'You think trust is earned through accountability and never inherited. That is what this star asks for.' },
  { low: 'You do not accept that belonging is primarily something practised rather than inherited. This is one of the sharper disagreements someone can have with the vision.',
    mid: 'You see belonging as partly practised and partly given, rather than one or the other.',
    high:'You think belonging is built through participation, not conferred at birth. That is this star’s whole claim.' },
  { low: 'You are more comfortable than this star with decisions being made centrally, perhaps because you think local judgement is inconsistent or capturable.',
    mid: 'You think decisions should sit close to their consequences in principle, with more exceptions than this star allows.',
    high:'You think decisions belong closest to the people who feel their consequences. That is exactly what this star argues.' },
  { low: 'You do not accept that natural monopolies belong in public hands. That is a substantial disagreement with the vision, and an argument this star is built to have.',
    mid: 'You are open to public ownership of some shared foundations, but not as a general rule.',
    high:'You think a market cannot discipline a monopoly, only extract from one, so the foundation should be publicly held.' },
  { low: 'You are not convinced the public should hold a permanent stake when it underwrites private risk. This star exists to argue the opposite.',
    mid: 'You are open to public and private sharing risk together, but not fully convinced public ownership should ever be locked in as a floor.',
    high:'You think public risk should earn a permanent public stake, with a floor that cannot be sold away.' },
  { low: 'You do not accept the case for unification, or you doubt distinct national identities could survive it. Both are arguments this star has to answer.',
    mid: 'You accept part of the tapestry — either the unified command or the preserved identities — but not both at once.',
    high:'You want one pattern woven from threads that keep their own colour: unified where it must be, distinct everywhere else.' }
];

const BANDS = [
  { max: 2, key: 'low',  label: 'Not aligned' },
  { max: 4, key: 'mid',  label: 'Mixed' },
  { max: 6, key: 'high', label: 'Aligned' }
];

const BSKY_PROFILE = 'https://bsky.app/profile/jpahonen.eurosky.social';

/* ------------------------------------------------------------------ helpers */

function esc(s) {
  const d = document.createElement('div');
  d.appendChild(document.createTextNode(s));
  return d.innerHTML;
}

function bandFor(score) {
  return BANDS.find(b => score <= b.max);
}

function encodeResult(scores) {
  return scores.map(s => String(Math.max(0, Math.min(6, s)))).join('');
}

/** Strictly validated: exactly seven digits, each 0-6. Anything else is ignored. */
function decodeResult(raw) {
  if (typeof raw !== 'string' || !/^[0-6]{7}$/.test(raw)) return null;
  return raw.split('').map(Number);
}

function resultUrl(scores) {
  const base = location.origin + location.pathname;
  return base + '?r=' + encodeResult(scores);
}

/* ------------------------------------------------------------- star diagram */

/* Geometry sized so the widest axis labels ("Belonging", "Commenda") clear the
   viewBox on both sides — they sit at ±0.975R horizontally on a seven-point ring. */
const CX = 240, CY = 200, R = 140;

function axisPoint(i, radius) {
  const angle = (-90 + i * (360 / 7)) * Math.PI / 180;
  return [CX + radius * Math.cos(angle), CY + radius * Math.sin(angle)];
}

function polyPoints(radii) {
  return radii.map((r, i) => axisPoint(i, r).map(n => n.toFixed(1)).join(',')).join(' ');
}

/** {7/3} star polygon — connect every third vertex for a sharp seven-pointed frame. */
function starFramePath(radius) {
  const order = [0, 3, 6, 2, 5, 1, 4];
  return order.map((v, idx) => {
    const [x, y] = axisPoint(v, radius);
    return (idx === 0 ? 'M' : 'L') + x.toFixed(1) + ',' + y.toFixed(1);
  }).join(' ') + ' Z';
}

function starChart(scores) {
  const rings = [1 / 3, 2 / 3, 1].map(f =>
    `<polygon class="ac-ring" points="${polyPoints(STARS.map(() => R * f))}"/>`).join('');

  const axes = STARS.map((_, i) => {
    const [x, y] = axisPoint(i, R);
    return `<line class="ac-axis" x1="${CX}" y1="${CY}" x2="${x.toFixed(1)}" y2="${y.toFixed(1)}"/>`;
  }).join('');

  const labels = STARS.map((s, i) => {
    const [x, y] = axisPoint(i, R + 24);
    const anchor = x > CX + 6 ? 'start' : (x < CX - 6 ? 'end' : 'middle');
    return `<text class="ac-label" x="${x.toFixed(1)}" y="${(y + 4).toFixed(1)}" text-anchor="${anchor}">${esc(s.short)}</text>`;
  }).join('');

  const dataRadii = scores.map(s => Math.max(6, (s / 6) * R));
  const dots = scores.map((s, i) => {
    const [x, y] = axisPoint(i, Math.max(6, (s / 6) * R));
    return `<circle class="ac-dot" cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="3.5"/>`;
  }).join('');

  const summary = STARS.map((s, i) => `${s.name}: ${scores[i]} of 6`).join('. ');

  return `<svg class="ac-chart" viewBox="0 0 480 420" role="img"
       aria-label="Your alignment across the seven stars. ${esc(summary)}.">
    <path class="ac-star-frame" d="${starFramePath(R)}"/>
    ${rings}
    ${axes}
    <polygon class="ac-shape" points="${polyPoints(dataRadii)}"/>
    ${dots}
    ${labels}
  </svg>`;
}

/* ----------------------------------------------------------------- rendering */

/* In a shared view the result belongs to someone else, so the readouts are
   rewritten into the third person. Every readout is authored in the second
   person with plural agreement ("you are"/"you think"), so the swap is exact. */
function thirdPerson(text) {
  return text.replace(/\bYou\b/g, 'They').replace(/\byou\b/g, 'they')
             .replace(/\bYour\b/g, 'Their').replace(/\byour\b/g, 'their');
}

function readoutList(scores, shared) {
  return STARS.map((s, i) => {
    const band = bandFor(scores[i]);
    const copy = shared ? thirdPerson(READOUTS[i][band.key]) : READOUTS[i][band.key];
    return `<li class="ac-readout ac-readout--${band.key}">
      <p class="ac-readout-head">
        <a href="/a-certain-vision/${s.slug}/">${esc(s.name)}</a>
        <span class="ac-band ac-band--${band.key}">${band.label} (${scores[i]}/6)</span>
      </p>
      <p class="ac-readout-body">${esc(copy)}</p>
    </li>`;
  }).join('');
}

function pushbackBlock(scores, shared) {
  const weak = STARS
    .map((s, i) => ({ s, i, score: scores[i] }))
    .filter(x => x.score <= 4)
    .sort((a, b) => a.score - b.score);

  if (!weak.length) {
    if (shared) return `<p class="ac-pushback">Every star landed for them. Yours may not — that is the interesting part.</p>`;
    return `<p class="ac-pushback">Every star landed for you. The argument still has to survive contact with people it did not persuade — if you know one, send them this.</p>`;
  }
  const links = weak.map(x =>
    `<a href="/a-certain-vision/${x.s.slug}/">${esc(x.s.name)} →</a>`).join(' ');
  if (shared) return `<p class="ac-pushback">These are the stars they pushed back on. The reasoning behind each one: ${links}</p>`;
  return `<p class="ac-pushback">If a star didn’t land for you, that’s exactly the kind of pushback this vision is built to take. Read the reasoning behind it: ${links}</p>`;
}

function shareBlock(scores) {
  const url = resultUrl(scores);
  let top = 0;
  scores.forEach((s, i) => { if (s > scores[top]) top = i; });
  const text = `My closest alignment with a certain vision of Europe: ${STARS[top].name}. Where do you land?\n\n${url}`;
  const intent = 'https://bsky.app/intent/compose?text=' + encodeURIComponent(text);
  return `<div class="ac-share">
    <a class="ac-btn" href="${esc(intent)}" target="_blank" rel="noopener">Share on Bluesky →</a>
    <button class="ac-btn ac-btn--ghost" type="button" data-copy="${esc(url)}">Copy link</button>
    <span class="ac-copied" role="status" aria-live="polite"></span>
  </div>
  <p class="ac-privacy">Your answers never leave this page. There is no cookie, no account, and no server storing any of this — the result lives only in that link.</p>`;
}

function renderResults(root, scores, shared) {
  root.innerHTML = `
    <section class="ac-results" aria-labelledby="ac-results-title">
      <h2 id="ac-results-title" class="headline-lg">${shared ? 'A shared result' : 'Your seven stars'}</h2>
      <p class="body-sm ac-intro">${shared
        ? 'Someone shared their alignment with you. This is their shape, not yours.'
        : 'No single score, on purpose. What matters is the shape — where you already agree, and where you’d argue.'}</p>
      ${starChart(scores)}
      <ol class="ac-readouts">${readoutList(scores, shared)}</ol>
      ${pushbackBlock(scores, shared)}
      ${shared
        ? `<p class="ac-share"><a class="ac-btn" href="${esc(location.pathname)}">Take it yourself →</a></p>`
        : shareBlock(scores)}
      <p class="meta ac-restart">${shared ? '' : `<a href="${esc(location.pathname)}">Start again</a> · `}<a href="/a-certain-vision/">Read the seven stars in full →</a></p>
    </section>`;
  root.querySelector('.ac-results').focus();
}

function renderQuiz(root) {
  const answers = new Array(QUESTIONS.length).fill(null);

  const questionsHtml = QUESTIONS.map((q, qi) => `
    <fieldset class="ac-q" data-q="${qi}">
      <legend class="ac-q-legend"><span class="ac-q-num">${qi + 1} / ${QUESTIONS.length}</span> ${esc(q.text)}</legend>
      <div class="ac-opts">
        ${OPTIONS.map(o => `
          <label class="ac-opt">
            <input type="radio" name="q${qi}" value="${o.value}">
            <span>${o.label}</span>
          </label>`).join('')}
      </div>
    </fieldset>`).join('');

  root.innerHTML = `
    <form class="ac-form" novalidate>
      <p class="ac-progress" role="status" aria-live="polite">0 of ${QUESTIONS.length} answered</p>
      ${questionsHtml}
      <div class="ac-submit">
        <button class="ac-btn" type="submit" disabled>See your seven stars →</button>
        <p class="ac-privacy">Nothing is stored and nothing is sent anywhere. The result exists only as a link you choose to share.</p>
      </div>
    </form>`;

  const form = root.querySelector('.ac-form');
  const progress = root.querySelector('.ac-progress');
  const submit = root.querySelector('.ac-submit button');

  form.addEventListener('change', e => {
    const m = /^q(\d+)$/.exec(e.target.name || '');
    if (!m) return;
    answers[Number(m[1])] = Number(e.target.value);
    e.target.closest('.ac-q').classList.add('is-answered');
    const done = answers.filter(a => a !== null).length;
    progress.textContent = `${done} of ${QUESTIONS.length} answered`;
    submit.disabled = done < QUESTIONS.length;
  });

  form.addEventListener('submit', e => {
    e.preventDefault();
    if (answers.some(a => a === null)) return;
    const scores = STARS.map((_, si) =>
      QUESTIONS.reduce((sum, q, qi) => sum + (q.star === si ? answers[qi] : 0), 0));
    history.replaceState(null, '', '?r=' + encodeResult(scores));
    renderResults(root, scores, false);
    root.scrollIntoView({ behavior: 'smooth', block: 'start' });
  });
}

function initAlignment() {
  const root = document.getElementById('alignment-app');
  if (!root) return;
  root.setAttribute('tabindex', '-1');

  const shared = decodeResult(new URLSearchParams(location.search).get('r'));
  if (shared) renderResults(root, shared, true);
  else renderQuiz(root);

  root.addEventListener('click', e => {
    const btn = e.target.closest('[data-copy]');
    if (!btn) return;
    const note = root.querySelector('.ac-copied');
    navigator.clipboard.writeText(btn.getAttribute('data-copy')).then(
      () => { if (note) note.textContent = 'Link copied'; },
      () => { if (note) note.textContent = 'Copy failed — select the address bar instead'; }
    );
  });
}

document.addEventListener('DOMContentLoaded', initAlignment);
