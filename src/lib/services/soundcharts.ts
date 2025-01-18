import { SOUNDCHARTS_API_KEY, SOUNDCHARTS_APP_ID } from '$env/static/private';
import type { ArtistMetadata, StreamingMetrics, SocialMetrics } from '$lib/types/stats';

const SOUNDCHARTS_BASE_URL = 'https://customer.api.soundcharts.com';

interface SoundchartsResponse<T> {
  data: T;
  meta?: {
    pagination?: {
      total: number;
      count: number;
      per_page: number;
      current_page: number;
      total_pages: number;
    };
  };
}

export class SoundchartsAPI {
  private apiKey: string;
  private appId: string;

  constructor() {
    this.apiKey = SOUNDCHARTS_API_KEY;
    this.appId = SOUNDCHARTS_APP_ID;
  }

  private async fetch<T>(endpoint: string, params?: Record<string, string>): Promise<T> {
    const url = new URL(`${SOUNDCHARTS_BASE_URL}${endpoint}`);
    console.log(url);
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        url.searchParams.append(key, value);
      });
    }

    const response = await fetch(url.toString(), {
      headers: {
        Accept: 'application/json',
        'x-app-id': this.appId,
        'x-api-key': this.apiKey,
      },
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Soundcharts API error: ${response.status} - ${errorText}`);
    }

    return response.json();
  }

  async getArtistStats(artistId: string) {
    const [artistMetadata] = await Promise.all([
      this.fetch<SoundchartsResponse<ArtistMetadata>>(`/api/v2/artist/${artistId}`),
      //   this.fetch<SoundchartsResponse<StreamingMetrics>>(`/api/v2/artist/${artistId}`),
      //   this.fetch<SoundchartsResponse<SocialMetrics>>(
      // `/api/v2.37/artist/${artistId}/social/instagram/followers`
      //   ),
    ]);

    return {
      metadata: artistMetadata,
      //   streaming: {
      //     streams: 0, // Placeholder since Soundcharts doesn't provide this directly
      //     listeners: 0,
      //     playlists: 0,
      //     shares: 0,
      //     views: 0,
      //     timestamp: Date.now(),
      //     platform: artistMetadata.data.object.name,
      //   },
      //   followers: {
      //     comments: socialStats.data.comments || 0,
      //     engagement: socialStats.data.engagement || 0,
      //     followers: socialStats.data.followers || 0,
      //     likes: socialStats.data.likes || 0,
      //     shares: socialStats.data.shares || 0,
      //     views: socialStats.data.views || 0,
      //     platform: socialStats.data.platform || 'instagram',
      //   },
    };
  }
}

export const soundcharts = new SoundchartsAPI();
