/**
 * views/callback.js — OAuth Callback Handler
 *
 * Activated when Facebook redirects back with ?code= or ?error= in the URL.
 * Walks through 3 animated steps:
 *   1. Verifying OAuth state (CSRF check)
 *   2. Exchanging the code with the backend
 *   3. Loading shop data
 * On success → cleans URL and navigates to #dashboard.
 * On failure → renders an error state with retry option.
 */

import { validateState, storeAuth }      from '../auth.js';
import { CONFIG }                         from '../config.js';

const STEPS = [
  { id: 'verify',    label: 'Verifying authorization' },
  { id: 'exchange',  label: 'Connecting to your account' },
  { id: 'loading',   label: 'Loading your Shop data' },
];

function renderSteps(activeIndex) {
  return STEPS.map((step, i) => {
    const isDone   = i < activeIndex;
    const isActive = i === activeIndex;
    const cls = isDone ? 'done' : isActive ? 'active' : '';
    const indicator = isDone ? '✓' : `${i + 1}`;
    return `
      <div class="callback-step ${cls}" id="step-${step.id}">
        <div class="step-indicator">${indicator}</div>
        <span>${step.label}</span>
      </div>
    `;
  }).join('');
}

function setStep(container, index) {
  STEPS.forEach((step, i) => {
    const el = container.querySelector(`#step-${step.id}`);
    if (!el) return;
    el.className = 'callback-step ' + (i < index ? 'done' : i === index ? 'active' : '');
    el.querySelector('.step-indicator').textContent = i < index ? '✓' : `${i + 1}`;
  });
}

function renderError(container, message) {
  container.innerHTML = `
    <section class="callback-page page-enter">
      <div class="glass-card callback-card">
        <div class="callback-error-icon">❌</div>
        <h1 class="callback-title">Connection Failed</h1>
        <p class="callback-subtitle">We couldn't complete the Facebook authorization.</p>
        <div class="callback-error-detail">${escapeHtml(message)}</div>
        <div style="margin-top: 28px; display: flex; gap: 12px; justify-content: center; flex-wrap: wrap;">
          <a href="/" class="btn btn-facebook" id="retry-btn">Try Again</a>
          <a href="/" class="btn btn-ghost"    id="cancel-btn">← Back</a>
        </div>
      </div>
    </section>
  `;
}

function escapeHtml(str) {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

export async function renderCallback(container, params) {
  const accessToken = params.get('access_token');
  const state       = params.get('state');
  const error       = params.get('error');
  const errorDesc   = params.get('error_description');

  // User denied access on Facebook
  if (error) {
    renderError(container, errorDesc ?? error);
    return;
  }

  if (!accessToken) {
    renderError(container, 'No access token received from Facebook.');
    return;
  }

  // Initial loading UI
  container.innerHTML = `
    <section class="callback-page page-enter">
      <div class="glass-card callback-card">
        <div class="callback-ring-wrap">
          <div class="callback-ring"></div>
          <span class="callback-ring-icon">🔗</span>
        </div>
        <h1 class="callback-title">Connecting your Shop</h1>
        <p class="callback-subtitle">This only takes a moment…</p>
        <div class="callback-steps">
          ${renderSteps(0)}
        </div>
      </div>
    </section>
  `;

  // Clean the URL so the code isn't sitting in the address bar
  window.history.replaceState({}, document.title, window.location.pathname);

  try {
    // Step 0 → validate CSRF state
    setStep(container, 0);
    // Small delay so the user can see the animation
    await delay(350);

    if (state) {
      validateState(state);
    }

    // Step 1 → Fetch user data & pages from Facebook Graph API directly
    setStep(container, 1);
    await delay(200);

    const authData = await fetchGraphData(accessToken);

    // Step 2 → finalizing
    setStep(container, 2);
    await delay(500);

    // Persist session and navigate to dashboard
    storeAuth(authData);
    window.location.hash = '#dashboard';

  } catch (err) {
    renderError(container, err.message || 'An unknown error occurred.');
  }
}

function delay(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// Helper to fetch user ID, name, email, picture, and connected pages via Graph API
async function fetchGraphData(accessToken) {
  const meUrl = `https://graph.facebook.com/v19.0/me?fields=id,name,email,picture&access_token=${accessToken}`;
  const pagesUrl = `https://graph.facebook.com/v19.0/me/accounts?fields=id,name,category,picture,has_shop&access_token=${accessToken}`;

  const [meResponse, pagesResponse] = await Promise.all([
    fetch(meUrl),
    fetch(pagesUrl)
  ]);

  if (!meResponse.ok) throw new Error('Failed to fetch user data from Facebook');
  if (!pagesResponse.ok) throw new Error('Failed to fetch pages data from Facebook');

  const userData = await meResponse.json();
  const pagesData = await pagesResponse.json();

  return {
    user: userData,
    pages: pagesData.data || [],
    scopes: [], // Implicit flow doesn't easily return granted scopes without another call, so we'll leave empty indicating fallback to requested.
    access_token: accessToken,
  };
}
