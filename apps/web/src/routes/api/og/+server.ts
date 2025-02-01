import { OGImage } from '$lib/components/og-image';
import type { RequestHandler } from '@sveltejs/kit';
import { ImageResponse } from '@vercel/og';

export const GET: RequestHandler = async ({ url }) => {
  const text = url.searchParams.get('text') ?? undefined;

  // We need to cast the JSX element to any because TypeScript in .ts files
  // doesn't understand JSX syntax
  const element = OGImage({ text }) as any;

  return new ImageResponse(element, {
    width: 1200,
    height: 630,
  });
};
