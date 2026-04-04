/**
 * auth.js — Facebook OAuth helpers + localStorage session management
 */

import { CONFIG } from './config.js';

const STORAGE_KEY = 'fb_shop_auth';
const STATE_KEY   = 'fb_oauth_state';

/** Returns true if the App ID is still the placeholder */
export function isConfigured() {
  return CONFIG.FACEBOOK_APP_ID !== 'YOUR_APP_ID_HERE';
}

/** Generate a cryptographically random state string to prevent CSRF */
function generateState() {
  const arr = new Uint8Array(16);
  crypto.getRandomValues(arr);
  return Array.from(arr, b => b.toString(16).padStart(2, '0')).join('');
}

/**
 * Builds the Facebook OAuth authorization URL and stores the CSRF state.
 * User is redirected here when they click "Connect with Facebook".
 */
export function buildOAuthUrl() {
  const state = generateState();
  sessionStorage.setItem(STATE_KEY, state);

  const params = new URLSearchParams({
    client_id:     CONFIG.FACEBOOK_APP_ID,
    redirect_uri:  CONFIG.REDIRECT_URI,
    scope:         CONFIG.SCOPES,
    response_type: 'token',
    state,
  });

  return `https://www.facebook.com/dialog/oauth?${params.toString()}`;
}

/**
 * Validates the state param returned by Facebook against the stored value.
 * Throws if they don't match (possible CSRF / replay attack).
 */
export function validateState(returnedState) {
  const stored = sessionStorage.getItem(STATE_KEY);
  sessionStorage.removeItem(STATE_KEY);
  if (!stored || stored !== returnedState) {
    throw new Error('OAuth state mismatch — possible CSRF attempt. Please try again.');
  }
}

/** Persist auth data from the backend response to localStorage */
export function storeAuth(data) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify({
    ...data,
    storedAt: Date.now(),
  }));
}

/** Retrieve the stored auth session, or null if none exists */
export function getStoredAuth() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

/** Clear the stored session (logout) */
export function clearAuth() {
  localStorage.removeItem(STORAGE_KEY);
}
