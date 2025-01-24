// Soundcharts API v2 Integration
// Documentation: https://doc.api.soundcharts.com/api/v2/doc

import { error } from '@sveltejs/kit';
import type { ArtistMetadata } from '$lib/types/stats';
import { SOUNDCHARTS_BASE_URL, SOUNDCHARTS_API_KEY, SOUNDCHARTS_APP_ID } from '$env/static/private';

// Core API Types
type SoundchartsErrorResponse = {
  key: string;
  code: number;
  message: string;
};

type SoundchartsPagination = {
  total: number;
  count: number;
  per_page: number;
  current_page: number;
  total_pages: number;
};

interface SoundchartsResponse<T> {
  data: T;
  meta?: {
    pagination?: SoundchartsPagination;
  };
  errors?: SoundchartsErrorResponse[];
}

// Domain Types
interface StreamingPlatformStats {
  monthlyListeners?: number;
  followers?: number;
  popularity?: number;
  playlists?: number;
  fans?: number;
}

interface StreamingStats {
  spotify: StreamingPlatformStats;
  appleMusic: StreamingPlatformStats;
  deezer: StreamingPlatformStats;
}

interface SocialPlatformStats {
  spotify: number;
  instagram: number;
  youtube: number;
  tiktok: number;
  facebook: number;
  twitter: number;
}

interface FollowersStats {
  total: number;
  platforms: SocialPlatformStats;
  history: Array<{ date: string; count: number }>;
}

interface Song {
  id: string;
  title: string;
  duration: number;
  releaseDate: string;
  isrc?: string;
}

type AlbumType = 'album' | 'ep' | 'single';

interface Album {
  id: string;
  title: string;
  type: AlbumType;
  releaseDate: string;
  trackCount: number;
  upc?: string;
}

interface Demographics {
  age: Array<{ range: string; percentage: number }>;
  gender: Array<{ type: string; percentage: number }>;
}

interface AudienceStats {
  demographics: Demographics;
  topCountries: Array<{ code: string; listeners: number }>;
}

type TrendDirection = 'up' | 'down' | 'stable';

interface PopularityStats {
  score: number;
  trend: TrendDirection;
  history: Array<{ date: string; score: number }>;
}

// API Response Types
interface BaseResponse<T, K extends string> {
  type: K;
  object: T;
  errors: string[];
}

type ArtistResponse = BaseResponse<ArtistMetadata, 'artist'>;
type StreamingResponse = BaseResponse<StreamingStats, 'streaming'>;
type FollowersResponse = BaseResponse<FollowersStats, 'followers'>;

// Default Response States
const defaultResponses = {
  metadata: {
    type: 'artist' as const,
    object: {
      uuid: '',
      slug: '',
      name: 'Unknown Artist',
      appUrl: '',
      imageUrl: '',
      countryCode: '',
      genres: [{ root: '', sub: [] }],
      biography: '',
      isni: '',
      ipi: '',
      gender: 'other',
      type: 'person',
      birthDate: '',
    },
    errors: [],
  },
  streaming: {
    type: 'streaming' as const,
    object: {
      spotify: { monthlyListeners: 0, followers: 0, popularity: 0, playlists: 0 },
      appleMusic: { playlists: 0 },
      deezer: { fans: 0, playlists: 0 },
    },
    errors: [],
  },
  followers: {
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
      history: [],
    },
    errors: [],
  },
} as const;

interface SoundchartsMetadata {
  name: string;
  image?: string;
  genres?: string[];
  country?: string;
}

interface SoundchartsStreaming {
  spotify_monthly_listeners?: number;
  spotify_followers?: number;
  youtube_subscribers?: number;
  youtube_views?: number;
}

interface SoundchartsSocial {
  instagram_followers?: number;
  twitter_followers?: number;
  tiktok_followers?: number;
  facebook_followers?: number;
}

export interface SoundchartsArtistStats {
  metadata: SoundchartsMetadata;
  streaming: SoundchartsStreaming;
  followers: SoundchartsSocial;
}

async function fetchFromSoundcharts(endpoint: string) {
  const response = await fetch(`${SOUNDCHARTS_API_BASE}${endpoint}`, {
    headers: {
      'x-api-key': SOUNDCHARTS_API_KEY,
      Accept: 'application/json',
    },
  });

  if (!response.ok) {
    if (response.status === 404) {
      return null;
    }
    throw new Error(`Soundcharts API error: ${response.statusText}`);
  }

  return response.json();
}

export async function getArtistStats(spotifyId: string): Promise<SoundchartsArtistStats | null> {
  try {
    const data = await fetchFromSoundcharts(`/artist/spotify/${spotifyId}`);
    if (!data) return null;

    // Transform the API response into our standardized format
    return {
      metadata: {
        name: data.name,
        image: data.image,
        genres: data.genres,
        country: data.country,
      },
      streaming: {
        spotify_monthly_listeners: data.platforms?.spotify?.monthlyListeners,
        spotify_followers: data.platforms?.spotify?.followers,
        youtube_subscribers: data.platforms?.youtube?.subscribers,
        youtube_views: data.platforms?.youtube?.views,
      },
      followers: {
        instagram_followers: data.platforms?.instagram?.followers,
        twitter_followers: data.platforms?.twitter?.followers,
        tiktok_followers: data.platforms?.tiktok?.followers,
        facebook_followers: data.platforms?.facebook?.followers,
      },
    };
  } catch (error) {
    console.error('Error fetching Soundcharts data:', error);
    return null;
  }
}

export async function searchArtist(query: string) {
  try {
    const data = await fetchFromSoundcharts(`/search/artist?q=${encodeURIComponent(query)}`);
    if (!data?.results) return [];

    return data.results.map((artist: any) => ({
      id: artist.id,
      name: artist.name,
      image: artist.image,
      spotifyId: artist.platforms?.spotify?.id,
    }));
  } catch (error) {
    console.error('Error searching Soundcharts:', error);
    return [];
  }
}

export class SoundchartsAPI {
  private readonly apiKey: string;
  private readonly appId: string;

  constructor() {
    if (!SOUNDCHARTS_API_KEY || !SOUNDCHARTS_APP_ID) {
      throw error(500, 'Missing required Soundcharts API credentials');
    }
    this.apiKey = SOUNDCHARTS_API_KEY;
    this.appId = SOUNDCHARTS_APP_ID;
  }

  /**
   * Verify JWT token from request headers
   * @param authHeader - Authorization header from request
   */
  private async verifyAuth(authHeader: string): Promise<boolean> {
    try {
      if (!authHeader?.startsWith('Bearer ')) {
        return false;
      }
      const token = authHeader.split(' ')[1];
      // Implement JWT verification here using this.serviceRoleKey
      // Return true if valid, false if invalid
      return true; // Placeholder - implement actual verification
    } catch (error) {
      console.error('Auth verification error:', error);
      return false;
    }
  }

  /**
   * Generic fetch method for Soundcharts API
   * Handles authentication and error responses
   * @param endpoint - API endpoint path
   * @param params - Optional query parameters
   */
  private async fetch<T>(endpoint: string, params?: Record<string, string>): Promise<T> {
    const url = new URL(`${SOUNDCHARTS_BASE_URL}${endpoint}`);

    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        url.searchParams.append(key, value);
      });
    }

    try {
      const response = await fetch(url.toString(), {
        headers: {
          Accept: 'application/json',
          'x-app-id': this.appId,
          'x-api-key': this.apiKey,
        },
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        throw error(response.status, {
          message: 'Soundcharts API error',
          details: errorData?.errors?.[0]?.message ?? 'Unknown error',
        });
      }

      return response.json();
    } catch (err) {
      if (err instanceof Error) {
        throw error(500, {
          message: 'Failed to fetch from Soundcharts API',
          details: err.message,
        });
      }
      throw err;
    }
  }

  /**
   * Get comprehensive artist statistics
   * Includes metadata, streaming stats, and social media followers
   * @param artistId - Soundcharts artist UUID
   */
  async getArtistStats(artistId: string) {
    try {
      const [metadataRes, streamingRes, followersRes] = await Promise.all([
        this.fetch<SoundchartsResponse<ArtistMetadata>>(`/api/v2.9/artist/${artistId}`),
        this.fetch<SoundchartsResponse<StreamingStats>>(`/api/v2/artist/${artistId}/streaming`),
        this.fetch<SoundchartsResponse<FollowersStats>>(`/api/v2/artist/${artistId}/followers`),
      ]);

      return {
        metadata: {
          ...defaultResponses.metadata,
          object: { ...defaultResponses.metadata.object, ...metadataRes.data },
        },
        streaming: {
          ...defaultResponses.streaming,
          object: { ...defaultResponses.streaming.object, ...streamingRes.data },
        },
        followers: {
          ...defaultResponses.followers,
          object: { ...defaultResponses.followers.object, ...followersRes.data },
        },
      };
    } catch (err) {
      console.error('Failed to fetch artist stats:', err);
      return defaultResponses;
    }
  }

  // Implement additional methods
  async getArtistSongs(artistId: string): Promise<Song[]> {
    try {
      const response = await this.fetch<SoundchartsResponse<Song[]>>(
        `/api/v2/artist/${artistId}/songs`
      );
      return response.data;
    } catch (err) {
      console.error('Failed to fetch artist songs:', err);
      return [];
    }
  }

  async getArtistAlbums(artistId: string): Promise<Album[]> {
    try {
      const response = await this.fetch<SoundchartsResponse<Album[]>>(
        `/api/v2/artist/${artistId}/albums`
      );
      return response.data;
    } catch (err) {
      console.error('Failed to fetch artist albums:', err);
      return [];
    }
  }

  async getArtistAudience(artistId: string): Promise<AudienceStats> {
    try {
      const response = await this.fetch<SoundchartsResponse<AudienceStats>>(
        `/api/v2/artist/${artistId}/audience`
      );
      return response.data;
    } catch (err) {
      console.error('Failed to fetch artist audience:', err);
      return {
        demographics: { age: [], gender: [] },
        topCountries: [],
      };
    }
  }

  async getArtistPopularity(artistId: string): Promise<PopularityStats> {
    try {
      const response = await this.fetch<SoundchartsResponse<PopularityStats>>(
        `/api/v2/artist/${artistId}/popularity`
      );
      return response.data;
    } catch (err) {
      console.error('Failed to fetch artist popularity:', err);
      return {
        score: 0,
        trend: 'stable',
        history: [],
      };
    }
  }

  async searchArtist(query: string): Promise<ArtistMetadata[]> {
    try {
      const response = await this.fetch<SoundchartsResponse<ArtistMetadata[]>>(
        '/api/v2/search/artists',
        { q: query }
      );
      return response.data;
    } catch (err) {
      console.error('Failed to search artists:', err);
      return [];
    }
  }
}

// Export singleton instance
export const soundcharts = new SoundchartsAPI();
