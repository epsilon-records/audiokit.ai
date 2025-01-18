import { SOUNDCHARTS_API_KEY } from '$env/static/private';

const SOUNDCHARTS_BASE_URL = 'https://api.soundcharts.com/api/v2';

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

  constructor() {
    this.apiKey = SOUNDCHARTS_API_KEY;
  }

  private async fetch<T>(endpoint: string, params?: Record<string, string>): Promise<T> {
    const url = new URL(`${SOUNDCHARTS_BASE_URL}${endpoint}`);
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        url.searchParams.append(key, value);
      });
    }

    const response = await fetch(url.toString(), {
      headers: {
        Accept: 'application/json',
        Authorization: `Bearer ${this.apiKey}`,
      },
    });

    if (!response.ok) {
      throw new Error(`Soundcharts API error: ${response.statusText}`);
    }

    return response.json();
  }

  async getArtistStats(artistId: string) {
    const [spotifyStats, socialStats] = await Promise.all([
      this.fetch<SoundchartsResponse<StreamingMetrics>>(`/artist/${artistId}/spotify/stats`),
      this.fetch<SoundchartsResponse<SocialMetrics>>(`/artist/${artistId}/social/stats`),
    ]);

    return {
      streaming: spotifyStats.data,
      social: socialStats.data,
    };
  }

  async getArtistRevenue(artistId: string, startDate: string, endDate: string) {
    return this.fetch<SoundchartsResponse<RevenueMetrics[]>>(`/artist/${artistId}/revenue`, {
      start_date: startDate,
      end_date: endDate,
    });
  }

  async searchArtist(query: string) {
    return this.fetch<SoundchartsResponse<Array<{ id: string; name: string }>>>('/search/artists', {
      q: query,
    });
  }
}

export const soundcharts = new SoundchartsAPI();
