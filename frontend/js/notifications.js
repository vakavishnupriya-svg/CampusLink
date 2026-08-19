/* Campus Event Pro - Notification Center Manager */

document.addEventListener('DOMContentLoaded', async () => {
  const notifContainer = document.getElementById('notifications-list');
  if (!notifContainer) return;

  const user = APIClient.getUser();
  if (!user) {
    window.location.href = '/frontend/login.html';
    return;
  }

  await loadNotifications();

  document.getElementById('mark-all-read-btn')?.addEventListener('click', async () => {
    try {
      await APIClient.request('/api/notifications/read-all', { method: 'PUT' });
      APIClient.showToast('All notifications marked as read', 'success');
      loadNotifications();
    } catch (err) {
      APIClient.showToast(err.message, 'error');
    }
  });
});

async function loadNotifications() {
  try {
    const notifications = await APIClient.request('/api/notifications');
    const container = document.getElementById('notifications-list');

    if (notifications.length === 0) {
      container.innerHTML = `
        <div style="text-align:center; padding:3rem; color:var(--text-muted);">
          <h3>No notifications yet</h3>
          <p style="font-size:0.9rem; margin-top:0.5rem;">Event updates and certificate alerts will appear here.</p>
        </div>
      `;
      return;
    }

    container.innerHTML = notifications.map(n => `
      <div class="glass-card" style="margin-bottom:1rem; border-left:4px solid ${n.is_read ? 'var(--border-color)' : 'var(--primary)'}; opacity:${n.is_read ? 0.75 : 1};">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.35rem;">
          <h4 style="font-size:1rem;">${n.title}</h4>
          <span style="font-size:0.75rem; color:var(--text-muted);">${new Date(n.created_at).toLocaleString()}</span>
        </div>
        <p style="font-size:0.9rem; color:var(--text-muted); margin-bottom:0.75rem;">${n.message}</p>
        <div style="display:flex; gap:0.5rem;">
          ${n.link ? `<a href="${n.link}" class="btn btn-secondary btn-sm">View Details</a>` : ''}
          ${!n.is_read ? `<button onclick="markRead(${n.id})" class="btn btn-outline btn-sm">Mark Read</button>` : ''}
          <button onclick="deleteNotif(${n.id})" class="btn btn-danger btn-sm" style="margin-left:auto;">Delete</button>
        </div>
      </div>
    `).join('');
  } catch (err) {
    console.error('Failed to load notifications', err);
  }
}

window.markRead = async function(id) {
  try {
    await APIClient.request(`/api/notifications/${id}/read`, { method: 'PUT' });
    loadNotifications();
  } catch (err) {
    APIClient.showToast(err.message, 'error');
  }
};

window.deleteNotif = async function(id) {
  try {
    await APIClient.request(`/api/notifications/${id}`, { method: 'DELETE' });
    APIClient.showToast('Notification deleted', 'info');
    loadNotifications();
  } catch (err) {
    APIClient.showToast(err.message, 'error');
  }
};
