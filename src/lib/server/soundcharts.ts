// Soundcharts API v2 Integration
// Documentation: https://doc.api.soundcharts.com/api/v2/doc

import { SOUNDCHARTS_API_KEY, SOUNDCHARTS_APP_ID } from '$env/static/private';
import type { ArtistMetadata } from '$lib/types/stats';

// Base URL for all Soundcharts API endpoints
const SOUNDCHARTS_BASE_URL = 'https://customer.api.soundcharts.com';

// Generic response type for Soundcharts API
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
  errors?: Array<{
    key: string;
    code: number;
    message: string;
  }>;
}

// Default artist metadata structure
const defaultMetadata = {
  type: 'artist' as const,
  object: {
    uuid: '',
    slug: '',
    name: 'Artist Name',
    appUrl: '',
    imageUrl: '',
    countryCode: '',
    genres: [{ root: '', sub: [] }],
    biography: '',
    isni: '',
    ipi: '',
    gender: 'other' as const,
    type: 'person' as const,
    birthDate: '',
  },
  errors: [],
};

// Default streaming statistics structure
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

// Default social media followers structure
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
    history: [] as Array<{ date: string; count: number }>,
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

  /**
   * Generic fetch method for Soundcharts API
   * Handles authentication and error responses
   * @param endpoint - API endpoint path
   * @param params - Optional query parameters
   */
  private async fetch<T>(endpoint: string, params?: Record<string, string>): Promise<T> {
    const url = new URL(`${SOUNDCHARTS_BASE_URL}${endpoint}`);

    // Add query parameters if provided
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        url.searchParams.append(key, value);
      });
    }

    // Make API request with required headers
    const response = await fetch(url.toString(), {
      headers: {
        Accept: 'application/json',
        'x-app-id': this.appId,
        'x-api-key': this.apiKey,
      },
    });

    // Handle API errors
    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Soundcharts API error: ${response.status} - ${errorText}`);
    }

    return response.json();
  }

  /**
   * Get comprehensive artist statistics
   * Includes metadata, streaming stats, and social media followers
   * @param artistId - Soundcharts artist UUID
   */
  async getArtistStats(artistId: string) {
    try {
      // Fetch artist metadata
      const metadata = await this.fetch<SoundchartsResponse<ArtistMetadata>>(
        `/api/v2.9/artist/${artistId}`
      );

      // TODO: Add additional API calls for streaming and followers data
      // const streaming = await this.fetch(`/api/v2/artist/${artistId}/streaming`);
      // const followers = await this.fetch(`/api/v2/artist/${artistId}/followers`);

      return {
        metadata: { ...defaultMetadata, ...metadata.data },
        streaming: { ...defaultStreaming },
        followers: { ...defaultFollowers },
      };
    } catch (error) {
      console.error('Error fetching artist stats:', error);
      // Return default values if API calls fail
      return {
        metadata: { ...defaultMetadata },
        streaming: { ...defaultStreaming },
        followers: { ...defaultFollowers },
      };
    }
  }

  // TODO: Add additional methods for other API endpoints:
  // - getArtistSongs(artistId: string)
  // - getArtistAlbums(artistId: string)
  // - getArtistAudience(artistId: string)
  // - getArtistPopularity(artistId: string)
  // - searchArtist(query: string)
}

// Export singleton instance
export const soundcharts = new SoundchartsAPI();
