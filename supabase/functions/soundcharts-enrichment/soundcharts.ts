interface StreamingResponse {
  type: 'streaming';
  object: {
    spotify: {
      monthlyListeners: number;
      followers: number;
      popularity: number;
      playlists: number;
    };
    appleMusic: {
      playlists: number;
    };
    deezer: {
      fans: number;
      playlists: number;
    };
  };
  errors: string[];
}

interface FollowersResponse {
  type: 'followers';
  object: {
    total: number;
    platforms: {
      spotify: number;
      instagram: number;
      youtube: number;
      tiktok: number;
      facebook: number;
      twitter: number;
    };
    history: Array<{
      date: string;
      total: number;
      platforms: {
        spotify?: number;
        instagram?: number;
        youtube?: number;
        tiktok?: number;
        facebook?: number;
        twitter?: number;
      };
    }>;
  };
  errors: string[];
}

interface MetadataResponse {
  type: 'artist';
  object: {
    uuid: string;
    slug: string;
    name: string;
    appUrl: string;
    imageUrl: string;
    countryCode: string;
    genres: Array<{
      root: string;
      sub: string[];
    }>;
    biography: string;
    isni: string;
    ipi: string;
    gender: 'male' | 'female' | 'other';
    type: 'person' | 'group';
    birthDate: string;
    location: string;
    websiteUrl: string;
    labels: string[];
    status: 'active' | 'inactive';
    createdAt: string;
    updatedAt: string;
  };
  errors: string[];
}

class Soundcharts {
  private apiKey: string;
  private appId: string;

  constructor(apiKey: string, appId: string) {
    this.apiKey = apiKey;
    this.appId = appId;
  }

  private async fetchWithAuth(endpoint: string) {
    const url = `https://customer.api.soundcharts.com/${endpoint}`;
    
    const response = await fetch(url, {
      headers: {
        'x-app-id': this.appId,
        'x-api-key': this.apiKey,
      },
    });

    if (!response.ok) {
      throw new Error(`Soundcharts API error for ${url}: ${response.statusText}`);
    }

    return response.json();
  }

  async getArtistStats(spotifyId: string) {
    const endpoints = [
      `api/v2.9/artist/by-platform/spotify/${spotifyId}`,
      `api/v2/artist/streaming/spotify/listening`,
      `api/v2.37/artist/social/spotify/followers`,
    ];

    const responses = await Promise.all(endpoints.map(endpoint => this.fetchWithAuth(endpoint)));

    const [metadata, streaming, followers] = responses;

    return {
      metadata,
      streaming,
      followers
    };
  }
}

// Initialize with environment variables
const apiKey = Deno.env.get('SOUNDCHARTS_API_KEY');
const appId = Deno.env.get('SOUNDCHARTS_APP_ID');

if (!apiKey || !appId) {
  throw new Error('Missing required environment variables: SOUNDCHARTS_API_KEY and/or SOUNDCHARTS_APP_ID');
}

export const soundcharts = new Soundcharts(apiKey, appId);