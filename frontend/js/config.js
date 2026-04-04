/**
 * config.js — App configuration
 *
 * ⚠️  SETUP REQUIRED:
 *  1. Register your app at https://developers.facebook.com/
 *  2. Create a "Business" type app and enable "Facebook Login"
 *  3. Add your redirect URI to "Valid OAuth Redirect URIs" in the app settings
 *  4. Replace FACEBOOK_APP_ID below with your numeric App ID
 */

export const CONFIG = {
  /**
   * Your Facebook Developer App ID.
   * Find it at: https://developers.facebook.com/apps/
   * Leave as-is to see the setup guide in the UI.
   */
  FACEBOOK_APP_ID: '547731668090451',

  /**
   * The URL Facebook will redirect back to after login.
   * Must EXACTLY match what you registered in Meta developer console.
   * For local dev: https://localhost:5173/
   */
  REDIRECT_URI: 'https://localhost:5173/',

  /**
   * Permissions (scopes) to request from the user.
   * Restored for End-to-End Shop Agent functionality.
   */
  SCOPES: [
    'email',
    'public_profile',
    'pages_show_list',
    'pages_read_engagement',
    'pages_messaging',
    'catalog_management'
  ].join(','),

  /**
   * Your backend server URL. The callback page will POST the auth
   * code here for server-side token exchange.
   * Endpoint expected: POST /api/auth/facebook/callback
   *   Body:    { code: string, redirect_uri: string }
   *   Returns: { user: { id, name, email, picture }, pages: [...], access_token: string }
   */
  BACKEND_URL: 'http://localhost:8000',
};
