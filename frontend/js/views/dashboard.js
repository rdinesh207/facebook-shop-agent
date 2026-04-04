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

function escapeHtml(str) {
  return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

/* Chat Bubble Renderer */
function createMessage(content, role = 'bot') {
  const isUser = role === 'user';
  const icon = isUser ? USER_ICON : BOT_ICON;
  const bubbleClass = isUser ? 'chat-bubble-user' : 'chat-bubble-bot';
  const wrapCls = isUser ? 'chat-msg-user-wrap' : 'chat-msg-bot-wrap';

  const div = document.createElement('div');
  div.className = `chat-msg ${wrapCls}`;
  div.innerHTML = `
    <div class="chat-avatar ${role}-avatar">${icon}</div>
    <div class="chat-bubble ${bubbleClass}">
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
          
          <div class="sidebar-section">
            <h4>SESSION TOKEN</h4>
            <div class="sidebar-token">${access_token || 'missing'}</div>
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
            <div class="chat-input-box">
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

  // Logout - using direct onclick to override any UI event blocking
  const logoutBtn = document.getElementById('logout-btn');
  if (logoutBtn) {
    logoutBtn.onclick = function(e) {
      e.preventDefault();
      if (confirm('Disconnect your Facebook account?')) {
        // Absolutely guarantee the token is removed
        localStorage.removeItem('fb_shop_auth');
        localStorage.clear(); // Clear anything else just in case
        
        // Force an immediate hash clear and hard reload
        window.location.hash = '';
        window.location.reload();
      }
    };
  }

  const chatContainer = document.getElementById('chat-messages');
  const textarea = document.getElementById('prompt-input');
  const sendBtn = document.getElementById('send-prompt-btn');

  function appendUserMessage(text) {
    if (!text.trim()) return;
    const msg = createMessage(escapeHtml(text), 'user');
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
    if (!text.trim()) return;
    
    // 1. Show user message
    textarea.value = '';
    textarea.style.height = 'auto'; // reset height
    appendUserMessage(text);
    
    // 2. Simulate AI thinking...
    const botTyping = createMessage('<span class="typing-indicator">...</span>', 'bot');
    chatContainer.appendChild(botTyping);
    scrollToBottom();

    await new Promise(r => setTimeout(r, 800));

    // 3. Remove typing, show response
    botTyping.remove();
    appendBotMessage(`<p>I've noted your request regarding "<em>${escapeHtml(text)}</em>".</p>
                      <p>Since the backend integration is pending, I can't fulfill this Graph API action yet, but your token is ready to send this request!</p>`);
  }

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
