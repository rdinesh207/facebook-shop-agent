/**
 * app.js — Main entry point & SPA router
 *
 * Routes:
 *   /                   → Landing page (if no auth) or Dashboard (if auth exists)
 *   /?code=...&state=.. → Callback handler (Facebook redirects here)
 *   #dashboard          → Dashboard (protected — redirects to landing if no auth)
 *
 * Uses hash-based routing for the dashboard, but the OAuth callback
 * comes in as query params on the base URL (no hash).
 */

import { getStoredAuth }         from './auth.js';
import { renderLanding }         from './views/landing.js';
import { renderCallback }        from './views/callback.js';
import { renderDashboard }       from './views/dashboard.js';

const app = document.getElementById('app');

/**
 * Determine the current route and render the matching view.
 */
function router() {
  // If user tries to manually type /dashboard instead of using hashes, force base URL
  if (window.location.pathname !== '/' && window.location.pathname !== '/index.html') {
    window.location.replace('/' + window.location.hash);
    return;
  }

  // Remove splash loader on first navigation
  const splash = document.getElementById('splash-loader');
  if (splash) splash.remove();

  const params = new URLSearchParams(window.location.search);
  const hash   = window.location.hash;

  // 1. Facebook OAuth callback - token response is in the hash fragment
  // Note: the Facebook implicit flow puts the token in the hash as access_token=...
  if (hash.includes('access_token=') || hash.includes('error=')) {
    // In implicit flow, facebook token is separated by '&' in the hash fragment.
    // E.g., #access_token=...&data_access_expiration_time=...&expires_in=...&state=...
    const hashStr = hash.replace(/^#/, '');
    const fragmentParams = new URLSearchParams(hashStr);

    // Call renderCallback with fragment params.
    renderCallback(app, fragmentParams);
    return;
  }

  // legacy query param check just in case.
  if (params.has('error')) {
    renderCallback(app, params);
    return;
  }

  // 2. Dashboard (hash route) — requires auth
  if (hash === '#dashboard') {
    const auth = getStoredAuth();
    if (auth) {
      renderDashboard(app, auth);
    } else {
      window.location.hash = '';
      renderLanding(app);
    }
    return;
  }

  // 3. Default — landing page (or redirect to dashboard if already authed)
  const auth = getStoredAuth();
  if (auth) {
    window.location.hash = '#dashboard';
    renderDashboard(app, auth);
    return;
  }

  renderLanding(app);
}

// Listen for hash changes (SPA navigation)
window.addEventListener('hashchange', router);

// Initial route on page load
router();
