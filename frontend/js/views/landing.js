/**
 * views/landing.js — Landing / Login page
 *
 * Shown when the user is not authenticated.
 * Renders the hero card with "Connect with Facebook" CTA,
 * feature pills, and a setup warning if the App ID is unconfigured.
 */

import { buildOAuthUrl, isConfigured } from '../auth.js';

/* Facebook 'f' logo as inline SVG */
const FB_LOGO_SVG = `
  <svg class="btn-icon" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
    <path d="M24 12.073C24 5.405 18.627 0 12 0S0 5.405 0 12.073C0 18.1 4.388 23.094 10.125 24v-8.437H7.078v-3.49h3.047V9.41c0-3.025 1.792-4.697 4.533-4.697 1.312 0 2.686.236 2.686.236v2.97h-1.513c-1.491 0-1.956.93-1.956 1.886v2.267h3.328l-.532 3.49h-2.796V24C19.612 23.094 24 18.1 24 12.073z"/>
  </svg>`;

/* Shop icon SVG */
const SHOP_SVG = `
  <svg width="22" height="22" viewBox="0 0 24 24" fill="white" aria-hidden="true">
    <path d="M19 7h-1V6a4 4 0 00-8 0v1H5a2 2 0 00-2 2v11a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2zm-7-3a2 2 0 012 2v1H8V6a2 2 0 012-2h2zm7 16H5V9h14v11z"/>
    <circle cx="9" cy="14" r="1.5"/>
    <circle cx="15" cy="14" r="1.5"/>
  </svg>`;

const FEATURES = [
  { icon: '🛍️', label: 'Product Management' },
  { icon: '🤖', label: 'AI Sales Assistance' },
  { icon: '📦', label: 'Inventory Sync' },
  { icon: '💬', label: 'Customer Interaction' },
  { icon: '📊', label: 'Analytics & Insights' },
  { icon: '🔄', label: 'Auto-Catalog Sync' },
];

export function renderLanding(container) {
  const configured = isConfigured();
  const oauthUrl   = configured ? buildOAuthUrl() : '#';

  container.innerHTML = `
    <section class="landing-page page-enter">

      <!-- Brand wordmark -->
      <div class="landing-logo">
        <div class="landing-logo-icon">${SHOP_SVG}</div>
        <span class="landing-logo-text">Facebook Shop Agent</span>
      </div>

      <!-- Hero card -->
      <div class="glass-card landing-card">
        <p class="landing-eyebrow">AI-Powered Commerce</p>

        <h1 class="landing-heading">
          Connect Your<br/>
          <span>Facebook Shop</span>
        </h1>

        <p class="landing-subtext">
          Automate your listings, sync inventory, and let AI handle customer
          interactions — all through your existing Facebook Business account.
        </p>

        <a
          id="connect-facebook-btn"
          href="${oauthUrl}"
          class="btn btn-facebook landing-connect-btn"
          ${!configured ? 'aria-disabled="true" style="opacity:0.45;cursor:not-allowed;pointer-events:none;"' : ''}
          role="button"
        >
          ${FB_LOGO_SVG}
          Continue with Facebook
        </a>

        <div class="landing-divider">
          <span>What you'll get access to</span>
        </div>

        <div class="landing-features">
          ${FEATURES.map(f => `
            <span class="badge badge-blue">
              <span>${f.icon}</span> ${f.label}
            </span>
          `).join('')}
        </div>
      </div>

      <!-- Setup guide — shown only when App ID is placeholder -->
      ${!configured ? `
        <div class="setup-notice" id="setup-notice" role="alert" aria-live="polite">
          <span class="setup-notice-icon">⚠️</span>
          <div class="setup-notice-body">
            <p class="setup-notice-title">Setup Required — Facebook App ID Missing</p>
            <p class="setup-notice-text">
              Before you can use the login flow, register a developer app and set your
              <code>FACEBOOK_APP_ID</code> in <code>js/config.js</code>.
            </p>
            <ol class="setup-steps">
              <li>Go to <strong>developers.facebook.com</strong> and sign in</li>
              <li>Click <strong>Create App</strong> → choose <em>Business</em> type</li>
              <li>Add <strong>Facebook Login</strong> as a product</li>
              <li>Under <em>Valid OAuth Redirect URIs</em>, add <code>http://localhost:3000/</code></li>
              <li>Copy your App ID into <code>js/config.js</code> → <code>FACEBOOK_APP_ID</code></li>
            </ol>
          </div>
        </div>
      ` : ''}

    </section>
  `;
}
