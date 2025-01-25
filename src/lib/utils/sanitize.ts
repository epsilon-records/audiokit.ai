export function sanitizeUrl(url: string | null | undefined): string {
  if (!url) return '';

  let sanitized = url.trim();

  // Add https:// if no protocol is present
  if (!sanitized.includes('://')) {
    sanitized = 'https://' + sanitized;
  }

  // Force https
  if (sanitized.startsWith('http://')) {
    sanitized = 'https://' + sanitized.slice(7);
  }

  // Remove www.
  sanitized = sanitized.replace(/^https?:\/\/www\./i, 'https://');

  try {
    const urlObj = new URL(sanitized);
    return urlObj.origin + urlObj.pathname;
  } catch {
    return '';
  }
}
