(function () {
  /* ── SIDEBAR BADGE (runs on every page with sidebar) ──────── */
  async function updateChatBadge() {
    try {
      const r = await fetch('/chat/unread/', { credentials: 'same-origin' });
      const data = await r.json();
      const badge = document.getElementById('chat-unread-badge');
      if (!badge) return;
      if (data.unread > 0) {
        badge.textContent = data.unread > 9 ? '9+' : data.unread;
        badge.style.display = 'inline-flex';
      } else {
        badge.style.display = 'none';
      }
    } catch {}
  }

  updateChatBadge();
  setInterval(updateChatBadge, 30000);

  /* ── CHAT ROOM (only on chat room page) ───────────────────── */
  const chatArea = document.getElementById('chat-messages');
  if (!chatArea) return;

  const RECIPIENT_ID = chatArea.dataset.recipientId;
  const SEND_URL = '/chat/send/';
  const POLL_URL = `/chat/poll/${RECIPIENT_ID}/`;
  let lastMsgId = 0;

  function getCsrf() {
    const m = document.cookie.match(/csrftoken=([^;]+)/);
    return m ? m[1] : '';
  }

  function escHtml(s) {
    return String(s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;')
      .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  function addBubble(msg) {
    const wrap = document.createElement('div');
    wrap.className = `bubble-wrap ${msg.is_mine ? 'mine' : 'theirs'}`;
    wrap.dataset.id = msg.id;
    wrap.innerHTML = `<div class="bubble">${escHtml(msg.text)}</div><span class="bubble-time">${escHtml(msg.created_at)}</span>`;
    chatArea.appendChild(wrap);
    chatArea.scrollTop = chatArea.scrollHeight;
    if (msg.id > lastMsgId) lastMsgId = msg.id;
  }

  async function pollMessages() {
    try {
      const r = await fetch(`${POLL_URL}?after=${lastMsgId}`, { credentials: 'same-origin' });
      const data = await r.json();
      data.messages.forEach(addBubble);
    } catch {}
  }

  async function sendMessage(text) {
    const fd = new FormData();
    fd.append('recipient_id', RECIPIENT_ID);
    fd.append('text', text);
    try {
      const r = await fetch(SEND_URL, {
        method: 'POST',
        credentials: 'same-origin',
        headers: { 'X-CSRFToken': getCsrf() },
        body: fd,
      });
      const data = await r.json();
      if (data.id) addBubble({ ...data, is_mine: true });
    } catch {}
  }

  const form = document.getElementById('chat-form');
  const input = document.getElementById('chat-input');

  form.addEventListener('submit', async e => {
    e.preventDefault();
    const text = input.value.trim();
    if (!text) return;
    input.value = '';
    input.focus();
    await sendMessage(text);
  });

  input.addEventListener('keydown', e => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      form.dispatchEvent(new Event('submit'));
    }
  });

  // Set initial lastMsgId from pre-rendered messages
  chatArea.querySelectorAll('.bubble-wrap[data-id]').forEach(el => {
    const id = parseInt(el.dataset.id || '0');
    if (id > lastMsgId) lastMsgId = id;
  });

  // Scroll to bottom on load
  chatArea.scrollTop = chatArea.scrollHeight;

  // Poll every 3s
  setInterval(pollMessages, 3000);
})();
