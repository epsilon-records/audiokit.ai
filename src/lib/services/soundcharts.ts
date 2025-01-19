import { SOUNDCHARTS_API_KEY, SOUNDCHARTS_APP_ID } from '$env/static/private';
import type { ArtistMetadata } from '$lib/types/stats';

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

const defaultMetadata = {
  type: 'artist' as const,
  object: {
    uuid: '',
    slug: '',
    name: 'Artist Name',
    appUrl: '',
    imageUrl: '',
    countryCode: '',
    genres: [
      {
        root: '',
        sub: [],
      },
    ],
    biography: '',
    isni: '',
    ipi: '',
    gender: 'other' as const,
    type: 'person' as const,
    birthDate: '',
  },
  errors: [],
};

const defaultStreaming = {
  type: 'streaming' as const,
  object: {
    spotify: {
      monthlyListeners: 0,
      followers: 0,
      popularity: 0,
      playlists: 0,
    },
    appleMusic: {
      playlists: 0,
    },
    deezer: {
      fans: 0,
      playlists: 0,
    },
  },
  errors: [],
};

const defaultFollowers = {
  type: 'followers' as const,
  object: {
    total: 0,
    platforms: {
      spotify: 0,
      instagram: 0,
      youtube: 0,
      tiktok: 0,
      facebook: 0,
      twitter: 0,
    },
    history: [] as { date: string; count: number }[],
  },
  errors: [],
};

export class SoundchartsAPI {
  private apiKey: string;
  private appId: string;

  constructor() {
    this.apiKey = SOUNDCHARTS_API_KEY;
    this.appId = SOUNDCHARTS_APP_ID;
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
      this.fetch<SoundchartsResponse<ArtistMetadata>>(`/api/v2.9/artist/${artistId}`),
    ]);

    return {
      metadata: artistMetadata,
      streaming: defaultStreaming,
      followers: defaultFollowers,
    };
  }
}

export const soundcharts = new SoundchartsAPI();
