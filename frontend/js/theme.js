/* Campus Event Pro - Dark/Light Theme Switcher */

document.addEventListener('DOMContentLoaded', () => {
  const currentTheme = localStorage.getItem('cep_theme') || 'dark';
  document.documentElement.setAttribute('data-theme', currentTheme);

  const themeToggles = document.querySelectorAll('.theme-toggle');
  themeToggles.forEach(toggle => {
    toggle.addEventListener('click', () => {
      const activeTheme = document.documentElement.getAttribute('data-theme');
      const newTheme = activeTheme === 'dark' ? 'light' : 'dark';
      document.documentElement.setAttribute('data-theme', newTheme);
      localStorage.setItem('cep_theme', newTheme);
    });
  });
});
