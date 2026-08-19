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
    const events = await APIClient.request('/api/events');
    const myRegistrations = events.filter(e => e.is_user_registered);
    const certificates = user.role === 'student' ? await APIClient.request('/api/certificates').catch(() => []) : [];
    
    // Date Calculations for counters
    const now = new Date();
    const todayStr = now.toISOString().split('T')[0];

    const upcomingEvents = events.filter(e => new Date(e.start_time) > now);
    const todaysEvents = events.filter(e => e.start_time.startsWith(todayStr));
    const totalRegistrations = events.reduce((sum, e) => sum + e.seats_taken, 0);

    // Update Counter Widgets
    document.getElementById('stat-total-events').textContent = events.length;
    document.getElementById('stat-upcoming-events').textContent = upcomingEvents.length;
    document.getElementById('stat-todays-events').textContent = todaysEvents.length;
    document.getElementById('stat-joined-events').textContent = myRegistrations.length;
    document.getElementById('stat-qr-count').textContent = totalRegistrations;
    document.getElementById('stat-certificates').textContent = certificates.length;

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

    // Initialize Chart.js Analytics
    renderDashboardCharts(events);

  } catch (err) {
    console.error("Dashboard error:", err);
  }
}

function renderDashboardCharts(events) {
  // Monthly Registration Trend Bar Chart
  const ctxMonthly = document.getElementById('chart-monthly-registrations')?.getContext('2d');
  if (ctxMonthly && typeof Chart !== 'undefined') {
    if (monthlyChartInstance) monthlyChartInstance.destroy();

    monthlyChartInstance = new Chart(ctxMonthly, {
      type: 'bar',
      data: {
        labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug'],
        datasets: [{
          label: 'Event Registrations',
          data: [65, 120, 95, 150, 210, 180, 240, 310],
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

  // Department Distribution Doughnut Chart
  const ctxDept = document.getElementById('chart-department-events')?.getContext('2d');
  if (ctxDept && typeof Chart !== 'undefined') {
    if (deptChartInstance) deptChartInstance.destroy();

    const deptCounts = {};
    events.forEach(e => {
      deptCounts[e.department] = (deptCounts[e.department] || 0) + 1;
    });

    const labels = Object.keys(deptCounts);
    const data = Object.values(deptCounts);

    deptChartInstance = new Chart(ctxDept, {
      type: 'doughnut',
      data: {
        labels: labels.length ? labels : ['CS', 'IT', 'Cultural', 'Sports'],
        datasets: [{
          data: data.length ? data : [4, 3, 2, 2],
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
