/* Campus Event Pro - Events Catalog, Smart Search & Action Menu */

let allEvents = [];

document.addEventListener('DOMContentLoaded', () => {
  const eventsGrid = document.getElementById('events-grid-catalog');
  if (!eventsGrid) return;

  setupSearchAndFilters();
  fetchEvents();
});

function setupSearchAndFilters() {
  const searchInput = document.getElementById('search-input');
  const catSelect = document.getElementById('filter-category');
  const deptSelect = document.getElementById('filter-department');
  const sortSelect = document.getElementById('filter-sort');

  let debounceTimer;
  if (searchInput) {
    searchInput.addEventListener('input', () => {
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(fetchEvents, 300);
    });
  }

  if (catSelect) catSelect.addEventListener('change', fetchEvents);
  if (deptSelect) deptSelect.addEventListener('change', fetchEvents);
  if (sortSelect) sortSelect.addEventListener('change', fetchEvents);
}

async function fetchEvents() {
  const search = document.getElementById('search-input')?.value || '';
  const category = document.getElementById('filter-category')?.value || 'All';
  const department = document.getElementById('filter-department')?.value || 'All';
  const sort_by = document.getElementById('filter-sort')?.value || 'newest';

  const params = new URLSearchParams();
  if (search) params.append('search', search);
  if (category !== 'All') params.append('category', category);
  if (department !== 'All') params.append('department', department);
  params.append('sort_by', sort_by);

  try {
    allEvents = await APIClient.request(`/api/events?${params.toString()}`);
    renderEvents(allEvents);
  } catch (err) {
    console.error('Failed to load events', err);
  }
}

function renderEvents(events) {
  const grid = document.getElementById('events-grid-catalog');
  if (!grid) return;

  const currentUser = APIClient.getUser();
  const isFacultyOrAdmin = currentUser && (currentUser.role === 'faculty' || currentUser.role === 'admin');

  if (events.length === 0) {
    grid.innerHTML = `
      <div style="grid-column: 1 / -1; text-align:center; padding: 4rem 1rem;">
        <h3 style="color:var(--text-muted);">No events found matching your search parameters</h3>
        <p style="color:var(--text-muted); font-size:0.9rem; margin-top:0.5rem;">Try clearing your search query or selecting a different category filter.</p>
      </div>
    `;
    return;
  }

  grid.innerHTML = events.map(ev => {
    const fillPercent = Math.min(100, Math.round((ev.seats_taken / ev.capacity) * 100));
    return `
      <div class="event-card">
        <img src="${ev.banner_url || 'https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=800&auto=format&fit=crop'}" alt="${ev.title}" class="event-banner" />
        <div class="event-card-body">
          <div class="event-card-meta">
            <span class="badge badge-${ev.category.toLowerCase()}">${ev.category}</span>
            <div style="display:flex; align-items:center; gap:0.5rem;">
              <button onclick="toggleBookmark(${ev.id}, event)" style="background:none; border:none; cursor:pointer; font-size:1.2rem;">
                ${ev.is_user_bookmarked ? '⭐' : '☆'}
              </button>
              ${isFacultyOrAdmin ? `
                <div style="position:relative; display:inline-block;">
                  <button onclick="toggleActionMenu(${ev.id})" style="background:none; border:none; cursor:pointer; color:var(--text-muted); font-weight:bold; font-size:1.2rem;">⋮</button>
                  <div id="action-menu-${ev.id}" style="display:none; position:absolute; right:0; top:100%; background:var(--bg-card); border:1px solid var(--border-glow); border-radius:var(--radius-md); box-shadow:var(--shadow-lg); z-index:100; min-width:140px; overflow:hidden;">
                    <a href="event-details.html?id=${ev.id}" style="display:block; padding:0.5rem 0.75rem; font-size:0.85rem;">👁️ View Details</a>
                    <button onclick="duplicateEvent(${ev.id})" style="width:100%; text-align:left; background:none; border:none; color:var(--text-main); padding:0.5rem 0.75rem; font-size:0.85rem; cursor:pointer;">📋 Duplicate</button>
                    <button onclick="deleteEventCard(${ev.id})" style="width:100%; text-align:left; background:none; border:none; color:var(--danger); padding:0.5rem 0.75rem; font-size:0.85rem; cursor:pointer;">🗑️ Delete</button>
                  </div>
                </div>
              ` : ''}
            </div>
          </div>
          <h3 class="event-card-title"><a href="event-details.html?id=${ev.id}">${ev.title}</a></h3>
          <p class="event-card-desc">${ev.description}</p>
          <div style="font-size:0.85rem; color:var(--text-muted); margin-bottom:0.5rem;">
            📍 ${ev.venue} | 📅 ${new Date(ev.start_time).toLocaleDateString()}
            ${ev.coordinator_name ? `<div style="font-size:0.8rem; color:#10b981; margin-top:0.25rem;">👨‍🏫 Coordinator: <b>${ev.coordinator_name}</b></div>` : ''}
          </div>
          <div class="progress-bar-wrap">
            <div style="display:flex; justify-content:space-between; font-size:0.75rem; color:var(--text-muted);">
              <span>Seats Occupancy</span>
              <span id="seat-count-${ev.id}">${ev.seats_taken}/${ev.capacity} (${fillPercent}%)</span>
            </div>
            <div class="progress-bar-track">
              <div id="seat-fill-${ev.id}" class="progress-bar-fill" style="width: ${fillPercent}%;"></div>
            </div>
          </div>
          <div style="margin-top:1rem; display:flex; gap:0.5rem;">
            <a href="event-details.html?id=${ev.id}" class="btn btn-secondary btn-sm" style="flex:1;">Details</a>
            ${ev.is_user_registered
              ? `<button class="btn btn-outline btn-sm" disabled style="opacity:0.7;">Registered ✓</button>`
              : `<button id="btn-register-${ev.id}" onclick="openRegistrationModal(${ev.id}, \`${ev.title.replace(/`/g, '\\`')}\`)" class="btn btn-primary btn-sm" style="flex:1;">Register</button>`
            }
          </div>
        </div>
      </div>
    `;
  }).join('');
}

window.toggleActionMenu = function(id) {
  const menu = document.getElementById(`action-menu-${id}`);
  if (menu) {
    menu.style.display = menu.style.display === 'block' ? 'none' : 'block';
  }
};

window.duplicateEvent = async function(id) {
  try {
    const dup = await APIClient.request(`/api/events/${id}/duplicate`, { method: 'POST' });
    APIClient.showToast(`Duplicated '${dup.title}'!`, 'success');
    fetchEvents();
  } catch (err) {
    APIClient.showToast(err.message, 'error');
  }
};

window.deleteEventCard = async function(id) {
  if (!confirm('Are you sure you want to delete this event?')) return;
  try {
    await APIClient.request(`/api/events/${id}`, { method: 'DELETE' });
    APIClient.showToast('Event deleted successfully', 'info');
    fetchEvents();
  } catch (err) {
    APIClient.showToast(err.message, 'error');
  }
};

window.toggleBookmark = async function(eventId, e) {
  e.preventDefault();
  if (!APIClient.getUser()) {
    window.location.href = 'login.html';
    return;
  }
  try {
    const res = await APIClient.request(`/api/events/${eventId}/bookmark`, { method: 'POST' });
    APIClient.showToast(res.message, 'success');
    fetchEvents();
  } catch (err) {
    APIClient.showToast(err.message, 'error');
  }
};

window.registerEventQuick = async function(eventId) {
  if (!APIClient.getUser()) {
    window.location.href = 'login.html';
    return;
  }
  try {
    const res = await APIClient.request(`/api/events/${eventId}/register`, { method: 'POST' });
    APIClient.showToast(`Registered successfully! QR Ticket generated.`, 'success');
    fetchEvents();
  } catch (err) {
    APIClient.showToast(err.message, 'error');
  }
};
