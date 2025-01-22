import { ImageResponse } from '@vercel/og';
import type { RequestHandler } from '@sveltejs/kit';

export const GET: RequestHandler = async () => {
  try {
    const html = `<div style="
      font-size: 40px;
      color: black;
      background: white;
      width: 100%;
      height: 100%;
      padding: 50px 200px;
      text-align: center;
      display: flex;
      justify-content: center;
      align-items: center;
    ">
      👋 Hello
    </div>`;

    const imageResponse = new ImageResponse(html, {
      width: 1200,
      height: 630,
    });

    // Convert ImageResponse to Response with correct headers
    return new Response(await imageResponse.arrayBuffer(), {
      headers: {
        'Content-Type': 'image/png',
        'Cache-Control': 'public, max-age=31536000, immutable',
      },
    });
  } catch (error) {
    console.error('Error generating OG image:', error);
    return new Response('Failed to generate image', { status: 500 });
  }
};
