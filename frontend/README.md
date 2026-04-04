# Facebook Shop Agent — Frontend

A single-page application that handles Facebook OAuth login for the Facebook Shop Agent.

## Architecture

```
frontend/
├── index.html              ← App shell (single HTML entry)
├── css/
│   └── styles.css          ← Design system (dark glassmorphism)
└── js/
    ├── app.js              ← SPA router & entry point
    ├── config.js           ← App ID, backend URL, scopes
    ├── auth.js             ← OAuth URL builder + session helpers
    ├── api.js              ← Backend API communication
    └── views/
        ├── landing.js      ← Login page with "Connect with Facebook"
        ├── callback.js     ← Handles OAuth redirect, sends code to backend
        └── dashboard.js    ← Authenticated dashboard (user, pages, scopes)
```

## Setup

### 1. Register a Facebook Developer App

1. Go to [developers.facebook.com](https://developers.facebook.com/)
2. Click **Create App** → Choose **Business** type
3. Add **Facebook Login** as a product
4. In Facebook Login → Settings → **Valid OAuth Redirect URIs**, add:
   ```
   http://localhost:3000/
   ```
5. Copy your **App ID** from the app dashboard

### 2. Configure the frontend

Open `js/config.js` and set your values:

```js
export const CONFIG = {
  FACEBOOK_APP_ID: '123456789012345',          // ← Your App ID
  REDIRECT_URI:    'http://localhost:3000/',    // ← Must match step 1.4
  BACKEND_URL:     'http://localhost:8000',     // ← Your backend server
  // ...
};
```

### 3. Run a local server

This is a vanilla HTML/CSS/JS app — no build step required. Just serve the files:

**Python:**
```bash
cd frontend
python -m http.server 3000
```

**Node.js (if you have it):**
```bash
npx -y serve -l 3000 frontend
```

**VS Code:** Install the [Live Server](https://marketplace.visualstudio.com/items?itemName=ritwickdey.LiveServer) extension and open `index.html`.

Then open [http://localhost:3000](http://localhost:3000) in your browser.

## Auth Flow

```
┌─────────┐     Click "Connect"     ┌──────────────────┐
│ Landing  │ ──────────────────────► │ facebook.com     │
│ Page     │                         │ /dialog/oauth    │
└─────────┘                         └────────┬─────────┘
                                              │ user approves
                                              ▼
┌─────────┐     POST { code }       ┌──────────────────┐
│ Callback │ ──────────────────────► │ Backend          │
│ Page     │                         │ /api/auth/fb/cb  │
│          │ ◄────────────────────── │                  │
│          │   { user, pages, token }└──────────────────┘
└────┬─────┘
     │ store session, navigate
     ▼
┌─────────┐
│Dashboard │  Shows user, pages, scopes, disconnect
└─────────┘
```

## Backend Contract

The callback page POSTs to `{BACKEND_URL}/api/auth/facebook/callback` with:

```json
{
  "code": "AQD...",
  "redirect_uri": "http://localhost:3000/"
}
```

Expected response (200 OK):

```json
{
  "user": {
    "id": "10230...",
    "name": "Jane Doe",
    "email": "jane@example.com",
    "picture": "https://..."
  },
  "pages": [
    {
      "id": "1234",
      "name": "My Shop",
      "category": "E-commerce Website",
      "has_shop": true,
      "picture": "https://..."
    }
  ],
  "scopes": ["email", "public_profile", "pages_show_list", "catalog_management"],
  "access_token": "EAAG..."
}
```
