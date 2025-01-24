// Soundcharts API v2 Integration
// Documentation: https://doc.api.soundcharts.com/api/v2/doc

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

// Add these interfaces after the SoundchartsResponse interface
interface StreamingStats {
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
}

interface FollowersStats {
  total: number;
  platforms: {
    spotify: number;
    instagram: number;
    youtube: number;
    tiktok: number;
    facebook: number;
    twitter: number;
  };
  history: Array<{ date: string; count: number }>;
}

interface Song {
  id: string;
  title: string;
  duration: number;
  releaseDate: string;
  isrc?: string;
}

interface Album {
  id: string;
  title: string;
  type: 'album' | 'ep' | 'single';
  releaseDate: string;
  trackCount: number;
  upc?: string;
}

interface AudienceStats {
  demographics: {
    age: Array<{ range: string; percentage: number }>;
    gender: Array<{ type: string; percentage: number }>;
  };
  topCountries: Array<{ code: string; listeners: number }>;
}

interface PopularityStats {
  score: number;
  trend: 'up' | 'down' | 'stable';
  history: Array<{ date: string; score: number }>;
}

// Define the base response type
interface BaseResponse<T, K extends string> {
  type: K;
  object: T;
  errors: string[];
}

// Define specific response types
type ArtistResponse = BaseResponse<ArtistMetadata, 'artist'>;
type StreamingResponse = BaseResponse<StreamingStats, 'streaming'>;
type FollowersResponse = BaseResponse<FollowersStats, 'followers'>;

// Update the default structures
const defaultMetadata: ArtistResponse = {
  type: 'artist',
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
    gender: 'other',
    type: 'person',
    birthDate: '',
  },
  errors: [],
};

const defaultStreaming: StreamingResponse = {
  type: 'streaming',
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

const defaultFollowers: FollowersResponse = {
  type: 'followers',
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
};

const SOUNDCHARTS_API_KEY = Deno.env.get("SOUNDCHARTS_API_KEY") ?? "";
const SOUNDCHARTS_APP_ID = Deno.env.get("SOUNDCHARTS_APP_ID") ?? "";
const SUPABASE_SERVICE_ROLE_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") ?? "";

export class SoundchartsAPI {
  private apiKey: string;
  private appId: string;
  private serviceRoleKey: string;

  constructor() {
    if (!SOUNDCHARTS_API_KEY || !SOUNDCHARTS_APP_ID || !SUPABASE_SERVICE_ROLE_KEY) {
      throw new Error("Missing required environment variables");
    }
    this.apiKey = SOUNDCHARTS_API_KEY;
    this.appId = SOUNDCHARTS_APP_ID;
    this.serviceRoleKey = SUPABASE_SERVICE_ROLE_KEY;
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
      const [metadataRes, streamingRes, followersRes] = await Promise.all([
        this.fetch<SoundchartsResponse<ArtistMetadata>>(`/api/v2.9/artist/${artistId}`),
        this.fetch<SoundchartsResponse<StreamingStats>>(`/api/v2/artist/${artistId}/streaming`),
        this.fetch<SoundchartsResponse<FollowersStats>>(`/api/v2/artist/${artistId}/followers`)
      ]);

      return {
        metadata: {
          ...defaultMetadata,
          object: { ...defaultMetadata.object, ...metadataRes.data }
        },
        streaming: {
          ...defaultStreaming,
          object: { ...defaultStreaming.object, ...streamingRes.data }
        },
        followers: {
          ...defaultFollowers,
          object: { ...defaultFollowers.object, ...followersRes.data }
        }
      };
    } catch (error) {
      console.error('Error fetching artist stats:', error);
      return {
        metadata: { ...defaultMetadata },
        streaming: { ...defaultStreaming },
        followers: { ...defaultFollowers }
      };
    }
  }

  // Implement additional methods
  async getArtistSongs(artistId: string) {
    try {
      const response = await this.fetch<SoundchartsResponse<Song[]>>(
        `/api/v2/artist/${artistId}/songs`
      );
      return response.data;
    } catch (error) {
      console.error('Error fetching artist songs:', error);
      return [];
    }
  }

  async getArtistAlbums(artistId: string) {
    try {
      const response = await this.fetch<SoundchartsResponse<Album[]>>(
        `/api/v2/artist/${artistId}/albums`
      );
      return response.data;
    } catch (error) {
      console.error('Error fetching artist albums:', error);
      return [];
    }
  }

  async getArtistAudience(artistId: string) {
    try {
      const response = await this.fetch<SoundchartsResponse<AudienceStats>>(
        `/api/v2/artist/${artistId}/audience`
      );
      return response.data;
    } catch (error) {
      console.error('Error fetching artist audience:', error);
      return {
        demographics: {
          age: [],
          gender: []
        },
        topCountries: []
      };
    }
  }

  async getArtistPopularity(artistId: string) {
    try {
      const response = await this.fetch<SoundchartsResponse<PopularityStats>>(
        `/api/v2/artist/${artistId}/popularity`
      );
      return response.data;
    } catch (error) {
      console.error('Error fetching artist popularity:', error);
      return {
        score: 0,
        trend: 'stable',
        history: []
      };
    }
  }

  async searchArtist(query: string) {
    try {
      const response = await this.fetch<SoundchartsResponse<ArtistMetadata[]>>(
        '/api/v2/search/artists',
        { q: query }
      );
      return response.data;
    } catch (error) {
      console.error('Error searching artists:', error);
      return [];
    }
  }
}

// Export singleton instance
export const soundcharts = new SoundchartsAPI();
