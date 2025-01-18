import { browser } from '$app/environment';

// Initialize theme from localStorage or system preference
function getInitialTheme() {
  if (!browser) return 'light';

  const stored = localStorage.getItem('theme');
  if (stored) return stored;

  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
}

// Create theme store
let theme = $state(getInitialTheme());

// Update HTML class and localStorage when theme changes
$effect(() => {
  if (!browser) return;

  const root = document.documentElement;
  if (theme === 'dark') {
    root.classList.add('dark');
  } else {
    root.classList.remove('dark');
  }

  localStorage.setItem('theme', theme);
});

// Export functions to get/set theme
export function getTheme() {
  return theme;
}

export function setTheme(newTheme: 'light' | 'dark') {
  theme = newTheme;
}

export function toggleTheme() {
  theme = theme === 'light' ? 'dark' : 'light';
}
