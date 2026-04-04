import { clearAuth } from '../auth.js';

/* — Icons — */
const FB_ICON = `
  <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
    <path d="M24 12.073C24 5.405 18.627 0 12 0S0 5.405 0 12.073C0 18.1 4.388 23.094 10.125 24v-8.437H7.078v-3.49h3.047V9.41c0-3.025 1.792-4.697 4.533-4.697 1.312 0 2.686.236 2.686.236v2.97h-1.513c-1.491 0-1.956.93-1.956 1.886v2.267h3.328l-.532 3.49h-2.796V24C19.612 23.094 24 18.1 24 12.073z"/>
  </svg>`;

const USER_ICON = `
  <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
    <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
  </svg>`;

const BOT_ICON = `
  <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
    <path d="M20 9V7c0-1.1-.9-2-2-2h-3c0-1.66-1.34-3-3-3S9 3.34 9 5H6c-1.1 0-2 .9-2 2v2c-1.66 0-3 1.34-3 3s1.34 3 3 3v4c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2v-4c1.66 0 3-1.34 3-3s-1.34-3-3-3zm-2 10H6V7h12v12zm-9-6c-.83 0-1.5-.67-1.5-1.5S8.17 10 9 10s1.5.67 1.5 1.5S9.83 13 9 13zm6 0c-.83 0-1.5-.67-1.5-1.5S14.17 10 15 10s1.5.67 1.5 1.5S15.83 13 15 13zm-8 3h8v2H7v-2z"/>
  </svg>`;

const SEND_ICON = `
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <line x1="22" y1="2" x2="11" y2="13"></line>
    <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
  </svg>`;

const ATTACH_ICON = `
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"></path>
  </svg>`;

function escapeHtml(str) {
  return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

/* Chat Bubble Renderer */
function createMessage(content, role = 'bot', imageUrl = null) {
  const isUser = role === 'user';
  const icon = isUser ? USER_ICON : BOT_ICON;
  const bubbleClass = isUser ? 'chat-bubble-user' : 'chat-bubble-bot';
  const wrapCls = isUser ? 'chat-msg-user-wrap' : 'chat-msg-bot-wrap';

  const div = document.createElement('div');
  div.className = `chat-msg ${wrapCls}`;

  let mediaHtml = '';
  if (imageUrl) {
    mediaHtml = `<div class="chat-media"><img src="${imageUrl}" class="chat-img-preview" /></div>`;
  }

  div.innerHTML = `
    <div class="chat-avatar ${role}-avatar">${icon}</div>
    <div class="chat-bubble ${bubbleClass}">
      ${mediaHtml}
      <div class="chat-text">${content}</div>
    </div>
  `;
  return div;
}

export function renderDashboard(container, authData) {
  const { user = {}, access_token } = authData;

  container.innerHTML = `
    <div class="chat-app page-enter">
      
      <!-- Top Navbar -->
      <nav class="chat-navbar">
        <div class="chat-nav-brand">
          <span class="chat-nav-logo">${BOT_ICON}</span>
          Facebook Shop Agent
        </div>
        <div class="chat-nav-actions">
          <span class="badge badge-green"><span class="dot"></span> Facebook Connected</span>
          <button class="nav-ghost-btn" id="logout-btn">Log Out</button>
        </div>
      </nav>

      <!-- Main Layout -->
      <div class="chat-layout">
        
        <!-- Sidebar (User session details) -->
        <aside class="chat-sidebar glass-card">
          <div class="sidebar-user">
            <img class="sidebar-avatar" src="${user.picture?.data?.url || ''}" onerror="this.style.display='none'" />
            <div class="sidebar-user-info">
              <span class="sidebar-name">${escapeHtml(user.name || 'Facebook User')}</span>
              <span class="sidebar-id">ID: ${user.id || 'Unknown'}</span>
            </div>
          </div>
          
        </aside>

        <!-- Main Chat Canvas -->
        <main class="chat-canvas">
          <div class="chat-scroll-area" id="chat-messages">
            
            <!-- Welcome Message (Bot) -->
            <div class="chat-msg chat-msg-bot-wrap">
              <div class="chat-avatar bot-avatar">${BOT_ICON}</div>
              <div class="chat-bubble chat-bubble-bot">
                <div class="chat-text">
                  <p>Welcome, <strong>${escapeHtml(user.name)}</strong>! Connection active.</p>
                  <p>I am your AI Shop Agent. I can help you manage your catalog, respond to messages, and analyze your inventory.</p>
                  <p>What would you like to do today?</p>
                </div>
                
                <div class="chat-suggestions">
                  <button class="suggestion-btn">Sync Inventory</button>
                  <button class="suggestion-btn">Draft Customer Reply</button>
                  <button class="suggestion-btn">List New Product</button>
                </div>
              </div>
            </div>

          </div>

          <!-- Chat Input Area -->
          <div class="chat-input-wrapper">
            <div id="image-preview-container" class="image-preview-container" style="display: none;">
               <!-- Preview injected here -->
            </div>
            <div class="chat-input-box">
              <button id="attach-btn" class="attach-btn" title="Attach Image">${ATTACH_ICON}</button>
              <input type="file" id="image-upload" accept="image/*" style="display: none;">
              <textarea id="prompt-input" rows="1" placeholder="Send a message to the agent..."></textarea>
              <button id="send-prompt-btn" aria-label="Send" class="send-btn">${SEND_ICON}</button>
            </div>
            <div class="chat-input-disclaimer">Shop Agent can make mistakes. Verify important actions.</div>
          </div>
        </main>
      </div>
    </div>
  `;

  // — Event Listeners —

  // Logout - instant native disconnect for prod-level UX (bypasses browser alert blocking)
  const logoutBtn = document.getElementById('logout-btn');
  if (logoutBtn) {
    logoutBtn.onclick = function (e) {
      e.preventDefault();

      // Guarantee destruction of the session
      localStorage.removeItem('fb_shop_auth');

      // Force an immediate hash clear and hard reload
      window.location.hash = '';
      window.location.reload();
    };
  }

  const chatContainer = document.getElementById('chat-messages');
  const textarea = document.getElementById('prompt-input');
  const sendBtn = document.getElementById('send-prompt-btn');
  const attachBtn = document.getElementById('attach-btn');
  const imageUpload = document.getElementById('image-upload');
  const previewContainer = document.getElementById('image-preview-container');

  const chatHistory = []; // Track chat history for the session
  let pendingImageBase64 = null;
  let pendingImageUrl = null;

  function appendUserMessage(text, imageUrl = null) {
    if (!text.trim() && !imageUrl) return;
    const msg = createMessage(escapeHtml(text), 'user', imageUrl);
    chatContainer.appendChild(msg);
    scrollToBottom();
  }

  function appendBotMessage(html) {
    const msg = createMessage(html, 'bot');
    chatContainer.appendChild(msg);
    scrollToBottom();
  }

  function scrollToBottom() {
    chatContainer.scrollTop = chatContainer.scrollHeight;
  }

  // Handle Form Submission
  async function submitPrompt() {
    const text = textarea.value;
    if (!text.trim() && !pendingImageBase64) return;

    // Capture current pending image
    const currentImageUrl = pendingImageUrl;
    const currentImageBase64 = pendingImageBase64;

    // 1. Show user message and clear input
    textarea.value = '';
    textarea.style.height = 'auto'; // reset height

    // Clear preview
    pendingImageBase64 = null;
    pendingImageUrl = null;
    previewContainer.style.display = 'none';
    previewContainer.innerHTML = '';

    appendUserMessage(text, currentImageUrl);

    // 2. Show thinking indicator
    const botTyping = createMessage('<span class="typing-indicator">...</span>', 'bot');
    chatContainer.appendChild(botTyping);
    scrollToBottom();

    try {
      // 3. Call actual backend
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: text,
          history: chatHistory,
          image: currentImageBase64
        })
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Backend unavailable');
      }

      const data = await response.json();

      // 4. Update history and UI
      botTyping.remove();
      chatHistory.push({ role: 'user', content: text });
      chatHistory.push({ role: 'assistant', content: data.response });

      appendBotMessage(data.response);
    } catch (err) {
      botTyping.remove();
      appendBotMessage(`<p style="color: #ef4444;"><strong>Error:</strong> ${err.message}. Make sure the backend is running at localhost:8000.</p>`);
    }
  }

  // Handle Image Upload
  attachBtn?.addEventListener('click', () => imageUpload.click());

  imageUpload?.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (event) => {
      pendingImageUrl = event.target.result;
      // Extract base64 without prefix for the backend
      pendingImageBase64 = event.target.result.split(',')[1];

      // Show preview
      previewContainer.style.display = 'flex';
      previewContainer.innerHTML = `
        <div class="preview-item">
          <img src="${pendingImageUrl}" />
          <button class="remove-preview-btn">✕</button>
        </div>
      `;

      previewContainer.querySelector('.remove-preview-btn').onclick = () => {
        pendingImageBase64 = null;
        pendingImageUrl = null;
        previewContainer.style.display = 'none';
        previewContainer.innerHTML = '';
        imageUpload.value = '';
      };
    };
    reader.readAsDataURL(file);
  });

  sendBtn?.addEventListener('click', submitPrompt);

  // Handle Enter key (Shift+Enter for newline)
  textarea?.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      submitPrompt();
    }
  });

  // Auto-resize textarea
  textarea?.addEventListener('input', () => {
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
  });

  // Suggestion buttons
  document.querySelectorAll('.suggestion-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      textarea.value = e.target.textContent;
      submitPrompt();
    });
  });
}
