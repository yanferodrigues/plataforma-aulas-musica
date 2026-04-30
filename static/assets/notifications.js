(function () {
  const API = '/accounts/notifications/';

  function getCsrf() {
    const m = document.cookie.match(/csrftoken=([^;]+)/);
    return m ? m[1] : '';
  }

  function escHtml(s) {
    return String(s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;')
      .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  function setBadge(count) {
    const badge = document.getElementById('notif-badge');
    if (!badge) return;
    if (count > 0) {
      badge.textContent = count > 9 ? '9+' : count;
      badge.style.display = 'flex';
    } else {
      badge.style.display = 'none';
    }
  }

  function renderList(notifications) {
    const list = document.getElementById('notif-list');
    if (!list) return;
    if (!notifications.length) {
      list.innerHTML = '<div class="notif-empty">Nenhuma notificação ainda.</div>';
      return;
    }
    list.innerHTML = notifications.map(n => `
      <div class="notif-item ${n.is_read ? '' : 'notif-unread'}">
        <div class="notif-item-subject">${escHtml(n.subject)}</div>
        <div class="notif-item-msg">${escHtml(n.message)}</div>
        <div class="notif-item-time">${escHtml(n.created_at)}</div>
      </div>
    `).join('');
  }

  async function fetchNotifs() {
    try {
      const r = await fetch(API, { credentials: 'same-origin' });
      return await r.json();
    } catch { return { notifications: [], unread: 0 }; }
  }

  async function markAllRead() {
    await fetch(API, {
      method: 'POST',
      credentials: 'same-origin',
      headers: { 'X-CSRFToken': getCsrf() },
    });
    setBadge(0);
    document.querySelectorAll('.notif-item.notif-unread').forEach(el => el.classList.remove('notif-unread'));
  }

  window.toggleNotifPanel = function () {
    const panel = document.getElementById('notif-panel');
    const backdrop = document.getElementById('notif-backdrop');
    if (!panel) return;
    const opening = !panel.classList.contains('open');
    panel.classList.toggle('open');
    backdrop.classList.toggle('open');

    if (opening) {
      const list = document.getElementById('notif-list');
      if (list) list.innerHTML = '<div class="notif-loading">Carregando…</div>';
      fetchNotifs().then(data => {
        renderList(data.notifications);
        if (data.unread > 0) markAllRead();
      });
    }
  };

  window.closeNotifPanel = function () {
    document.getElementById('notif-panel')?.classList.remove('open');
    document.getElementById('notif-backdrop')?.classList.remove('open');
  };

  window.markAllRead = markAllRead;

  // Badge on page load
  fetchNotifs().then(data => setBadge(data.unread));
})();
