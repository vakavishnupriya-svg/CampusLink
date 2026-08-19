/* Campus Event Pro - Central API Client */

const API_BASE_URL = (window.location.origin.includes('localhost') || window.location.origin.includes('127.0.0.1'))
  ? (window.location.port === '8000' ? '' : 'http://127.0.0.1:8000')
  : '';

class APIClient {
  static getToken() {
    return localStorage.getItem('cep_access_token');
  }

  static setToken(token) {
    localStorage.setItem('cep_access_token', token);
  }

  static removeToken() {
    localStorage.removeItem('cep_access_token');
    localStorage.removeItem('cep_user');
  }

  static getUser() {
    const userStr = localStorage.getItem('cep_user');
    return userStr ? JSON.parse(userStr) : null;
  }

  static setUser(user) {
    localStorage.setItem('cep_user', JSON.stringify(user));
  }

  static async request(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const token = this.getToken();

    const headers = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const config = {
      ...options,
      headers,
    };

    try {
      const response = await fetch(url, config);
      
      if (response.status === 401) {
        this.removeToken();
        if (!window.location.pathname.includes('login.html') && !window.location.pathname.includes('register.html') && window.location.pathname !== '/' && window.location.pathname !== '/index.html') {
          window.location.href = 'login.html';
        }
      }

      const data = await response.json().catch(() => ({}));

      if (!response.ok) {
        throw new Error(data.detail || 'An error occurred while processing your request');
      }

      return data;
    } catch (err) {
      console.error(`API Error [${endpoint}]:`, err);
      throw err;
    }
  }

  static showToast(message, type = 'info') {
    let container = document.getElementById('toast-container');
    if (!container) {
      container = document.createElement('div');
      container.id = 'toast-container';
      document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `<span class="toast-message">${message}</span>`;

    container.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateX(100%)';
      setTimeout(() => toast.remove(), 300);
    }, 4000);
  }
}
