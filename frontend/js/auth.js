/* Campus Event Pro - Authentication Manager */

document.addEventListener('DOMContentLoaded', () => {
  AuthManager.updateNavigation();
  AuthManager.setupAuthForms();
});

class AuthManager {
  static updateNavigation() {
    const user = APIClient.getUser();
    const navActions = document.querySelector('.nav-actions');
    const navLinks = document.querySelector('.nav-links');

    if (!navActions) return;

    if (user) {
      // Dynamic Role Link additions
      let roleSpecificLink = '';
      if (user.role === 'faculty' || user.role === 'admin') {
        roleSpecificLink = `<li><a href="create-event.html" class="nav-link">+ Create Event</a></li>`;
      }
      if (user.role === 'teacher_coordinator' || user.role === 'teacher') {
        roleSpecificLink += `<li><a href="teacher-dashboard.html" class="nav-link">Teacher Portal</a></li>`;
      }
      if (user.role === 'admin') {
        roleSpecificLink += `<li><a href="admin.html" class="nav-link">Admin Portal</a></li>`;
      }

      if (navLinks) {
        const existingLinks = `
          <li><a href="index.html" class="nav-link">Home</a></li>
          <li><a href="calendar.html" class="nav-link">Calendar</a></li>
          <li><a href="events.html" class="nav-link">Events</a></li>
          <li><a href="dashboard.html" class="nav-link">Dashboard</a></li>
          ${roleSpecificLink}
        `;
        navLinks.innerHTML = existingLinks;
      }

      navActions.innerHTML = `
        <a href="notifications.html" class="btn btn-secondary btn-sm" title="Notifications">
          🔔 <span id="nav-notif-badge" class="badge badge-tech" style="display:none;">0</span>
        </a>
        <a href="profile.html" class="btn btn-secondary btn-sm">
          👤 ${user.full_name ? user.full_name.split(' ')[0] : 'User'}
        </a>
        <button id="logout-btn" class="btn btn-outline btn-sm">Logout</button>
      `;

      const logoutBtn = document.getElementById('logout-btn');
      if (logoutBtn) {
        logoutBtn.addEventListener('click', () => {
          APIClient.removeToken();
          APIClient.showToast('Logged out successfully', 'info');
          setTimeout(() => window.location.href = 'login.html', 500);
        });
      }

      // Sync Notifications count
      this.fetchNotificationCount();
    } else {
      navActions.innerHTML = `
        <a href="login.html" class="btn btn-secondary btn-sm">Log In</a>
        <a href="register.html" class="btn btn-primary btn-sm">Register</a>
      `;
    }
  }

  static async fetchNotificationCount() {
    try {
      const notifs = await APIClient.request('/api/notifications');
      const unread = notifs.filter(n => !n.is_read).length;
      const badge = document.getElementById('nav-notif-badge');
      if (badge && unread > 0) {
        badge.textContent = unread;
        badge.style.display = 'inline-flex';
      }
    } catch (e) {
      // Ignore background sync errors
    }
  }

  static setupAuthForms() {
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
      loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const email = document.getElementById('login-email')?.value.trim();
        const password = document.getElementById('login-password')?.value;

        if (!email || !password) {
          APIClient.showToast('Please enter both email and password', 'error');
          return;
        }

        try {
          const body = new URLSearchParams();
          body.append('username', email);
          body.append('password', password);

          const res = await fetch(`${API_BASE_URL}/api/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: body
          });

          const data = await res.json();
          if (!res.ok) throw new Error(data.detail || 'Login failed');

          APIClient.setToken(data.access_token);
          APIClient.setUser(data.user);
          APIClient.showToast(`Welcome back, ${data.user.full_name}!`, 'success');

          setTimeout(() => {
            if (data.user.role === 'admin') {
              window.location.href = 'admin.html';
            } else if (data.user.role === 'teacher_coordinator' || data.user.role === 'teacher') {
              window.location.href = 'teacher-dashboard.html';
            } else {
              window.location.href = 'dashboard.html';
            }
          }, 600);
        } catch (err) {
          APIClient.showToast(err.message, 'error');
        }
      });
    }

    const registerForm = document.getElementById('register-form');
    if (registerForm) {
      registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const role = document.getElementById('reg-role')?.value || 'student';
        
        if (role === 'teacher_coordinator') {
          const name = document.getElementById('reg-name')?.value.trim();
          const employee_id = document.getElementById('reg-emp-id')?.value.trim();
          const email = document.getElementById('reg-email')?.value.trim();
          const phone = document.getElementById('reg-phone')?.value.trim();
          const department = document.getElementById('reg-dept')?.value;
          const password = document.getElementById('reg-password')?.value;
          const confirm_password = document.getElementById('reg-confirm-password')?.value;

          if (!name || !employee_id || !email || !phone || !password || !confirm_password) {
            APIClient.showToast('Please fill out all required fields.', 'error');
            return;
          }

          if (password !== confirm_password) {
            APIClient.showToast('Password and Confirm Password do not match.', 'error');
            return;
          }

          try {
            const res = await APIClient.request('/api/auth/register-teacher', {
              method: 'POST',
              body: JSON.stringify({ name, employee_id, email, phone, department, password, confirm_password })
            });

            APIClient.showToast(res.message, 'success');
            setTimeout(() => window.location.href = 'login.html', 1500);
          } catch (err) {
            APIClient.showToast(err.message, 'error');
          }
        } else {
          const full_name = document.getElementById('reg-name')?.value.trim();
          const email = document.getElementById('reg-email')?.value.trim();
          const phone = document.getElementById('reg-phone')?.value.trim();
          const department = document.getElementById('reg-dept')?.value;
          const roll_number = document.getElementById('reg-roll')?.value.trim();
          const password = document.getElementById('reg-password')?.value;

          if (!full_name || !email || !phone || !roll_number || !password) {
            APIClient.showToast('Please fill out all required fields: Full Name, Email, Phone Number, Roll Number, and Password.', 'error');
            return;
          }

          if (phone.length !== 10 || isNaN(phone)) {
            APIClient.showToast('Phone number must contain exactly 10 digits.', 'error');
            return;
          }

          try {
            const res = await APIClient.request('/api/auth/register', {
              method: 'POST',
              body: JSON.stringify({ full_name, email, phone, password, role: 'student', department, roll_number })
            });

            APIClient.setToken(res.access_token);
            APIClient.setUser(res.user);
            APIClient.showToast('Registration successful', 'success');
            setTimeout(() => window.location.href = 'dashboard.html', 600);
          } catch (err) {
            APIClient.showToast(err.message, 'error');
          }
        }
      });
    }
  }
}
