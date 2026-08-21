/* Campus Event Pro - Dashboard Controller with Chart.js */

let monthlyChartInstance = null;
let deptChartInstance = null;

document.addEventListener('DOMContentLoaded', async () => {
  const dashboardContainer = document.getElementById('dashboard-view');
  if (!dashboardContainer) return;

  const user = APIClient.getUser();
  if (!user) {
    window.location.href = 'login.html';
    return;
  }

  // Populate user profile info
  document.getElementById('user-name-display').textContent = user.full_name;
  document.getElementById('user-role-badge').textContent = user.role.toUpperCase();
  document.getElementById('user-dept-display').textContent = user.department;
  if (user.avatar_url) {
    document.getElementById('user-avatar-img').src = user.avatar_url;
  }

  await loadDashboardData(user);
});

async function loadDashboardData(user) {
  try {
    const stats = await APIClient.request('/api/dashboard/stats').catch(() => null);
    const events = await APIClient.request('/api/events');
    const myRegistrations = events.filter(e => e.is_user_registered);

    // Update Counter Widgets using live database data
    if (stats) {
      if (document.getElementById('stat-total-students')) document.getElementById('stat-total-students').textContent = stats.total_students;
      if (document.getElementById('stat-total-teachers')) document.getElementById('stat-total-teachers').textContent = stats.total_teachers;
      if (document.getElementById('stat-total-events')) document.getElementById('stat-total-events').textContent = stats.total_events;
      if (document.getElementById('stat-total-registrations')) document.getElementById('stat-total-registrations').textContent = stats.total_registrations;
      if (document.getElementById('stat-upcoming-events')) document.getElementById('stat-upcoming-events').textContent = stats.upcoming_events;
      if (document.getElementById('stat-recent-registrations-count')) document.getElementById('stat-recent-registrations-count').textContent = stats.recent_registrations.length;
    } else {
      const now = new Date();
      document.getElementById('stat-total-events').textContent = events.length;
      document.getElementById('stat-upcoming-events').textContent = events.filter(e => new Date(e.start_time) > now).length;
      document.getElementById('stat-total-registrations').textContent = events.reduce((sum, e) => sum + e.seats_taken, 0);
    }

    // Render Registered Tickets List
    const joinedList = document.getElementById('joined-events-list');
    if (joinedList) {
      if (myRegistrations.length === 0) {
        joinedList.innerHTML = `
          <div class="glass-card" style="text-align:center; padding:2rem;">
            <p style="color:var(--text-muted);">You haven't registered for any events yet.</p>
            <a href="events.html" class="btn btn-primary btn-sm" style="margin-top:1rem;">Explore Events</a>
          </div>
        `;
      } else {
        joinedList.innerHTML = myRegistrations.map(ev => `
          <div class="ticket-item">
            <div class="ticket-info">
              <h4>${ev.title}</h4>
              <p>📅 ${new Date(ev.start_time).toLocaleString()} | 📍 ${ev.venue}</p>
            </div>
            <a href="event-details.html?id=${ev.id}" class="btn btn-secondary btn-sm">View QR Ticket</a>
          </div>
        `).join('');
      }
    }

    // Render Recent Activity Feed with actual recent registrations
    const activityFeed = document.getElementById('activity-feed-container');
    if (activityFeed && stats && stats.recent_registrations && stats.recent_registrations.length > 0) {
      activityFeed.innerHTML = `
        <div class="glass-card" style="padding:1rem;">
          ${stats.recent_registrations.map(r => `
            <div class="ticket-item" style="margin-bottom:0.5rem; padding:0.6rem; background:rgba(255,255,255,0.03); border-radius:6px;">
              <div class="ticket-info">
                <h4 style="font-size:0.95rem;">👤 ${r.full_name} <small style="color:var(--text-muted);">(${r.roll_no})</small></h4>
                <p style="font-size:0.8rem; color:var(--primary);">Registered for <b>${r.event_name}</b></p>
                <small style="font-size:0.75rem; color:var(--text-muted);">${r.registered_at ? new Date(r.registered_at).toLocaleString() : ''}</small>
              </div>
            </div>
          `).join('')}
        </div>
      `;
    }

    // Initialize Chart.js Analytics using live database data
    renderDashboardCharts(events, stats);

  } catch (err) {
    console.error("Dashboard error:", err);
  }
}

function renderDashboardCharts(events, stats) {
  // Monthly Registration Trend Bar Chart (Live DB Data)
  const ctxMonthly = document.getElementById('chart-monthly-registrations')?.getContext('2d');
  if (ctxMonthly && typeof Chart !== 'undefined') {
    if (monthlyChartInstance) monthlyChartInstance.destroy();

    const monthlyLabels = stats && stats.monthly_registrations ? stats.monthly_registrations.map(m => m.month) : ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    const monthlyCounts = stats && stats.monthly_registrations ? stats.monthly_registrations.map(m => m.count) : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0];

    monthlyChartInstance = new Chart(ctxMonthly, {
      type: 'bar',
      data: {
        labels: monthlyLabels,
        datasets: [{
          label: 'Event Registrations',
          data: monthlyCounts,
          backgroundColor: 'rgba(99, 102, 241, 0.7)',
          borderColor: '#6366f1',
          borderWidth: 2,
          borderRadius: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94a3b8' } },
          y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94a3b8' } }
        }
      }
    });
  }

  // Department Distribution Doughnut Chart (Live DB Data)
  const ctxDept = document.getElementById('chart-department-events')?.getContext('2d');
  if (ctxDept && typeof Chart !== 'undefined') {
    if (deptChartInstance) deptChartInstance.destroy();

    let labels = [];
    let data = [];

    if (stats && stats.department_stats && stats.department_stats.length > 0) {
      labels = stats.department_stats.map(d => d.department);
      data = stats.department_stats.map(d => d.count);
    } else {
      const deptCounts = {};
      events.forEach(e => {
        deptCounts[e.department] = (deptCounts[e.department] || 0) + 1;
      });
      labels = Object.keys(deptCounts);
      data = Object.values(deptCounts);
    }

    deptChartInstance = new Chart(ctxDept, {
      type: 'doughnut',
      data: {
        labels: labels.length ? labels : ['Computer Science', 'Information Technology', 'Electrical Engineering'],
        datasets: [{
          data: data.length ? data : [1, 1, 1],
          backgroundColor: ['#6366f1', '#8b5cf6', '#ec4899', '#10b981', '#f59e0b', '#0ea5e9'],
          borderWidth: 2,
          borderColor: '#0f172a'
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: 'right', labels: { color: '#94a3b8', font: { size: 11 } } }
        }
      }
    });
  }
}
