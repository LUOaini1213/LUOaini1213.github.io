(() => {
  'use strict';
  const root = document.documentElement;
  const button = document.querySelector('.case-theme');
  let saved;
  try { saved = localStorage.getItem('theme'); } catch (_) { /* Storage may be disabled. */ }
  const dark = saved === 'dark' || (!saved && matchMedia('(prefers-color-scheme: dark)').matches);
  function setTheme(isDark) {
    root.setAttribute('data-theme', isDark ? 'dark' : 'light');
    button.setAttribute('aria-pressed', String(isDark));
  }
  setTheme(dark);
  button.addEventListener('click', () => {
    const isDark = root.getAttribute('data-theme') !== 'dark';
    setTheme(isDark);
    try { localStorage.setItem('theme', isDark ? 'dark' : 'light'); } catch (_) { /* Theme still changes without storage. */ }
  });
  const language = document.querySelector('.case-language');
  language.addEventListener('click', () => {
    language.href = language.getAttribute('href').split('#')[0] + window.location.hash;
  });
})();
