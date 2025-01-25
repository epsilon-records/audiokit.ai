export function sanitizeUrl(url: string | null | undefined): string {
  if (!url) return '';

  let sanitized = url.trim();

  // Remove any query parameters and fragments
  sanitized = sanitized.split('?')[0].split('#')[0];

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

    // Validate the URL structure
    if (!urlObj.hostname || !urlObj.protocol.match(/^https?:$/)) {
      return '';
    }

    return urlObj.origin + urlObj.pathname;
  } catch {
    return '';
  }
}
