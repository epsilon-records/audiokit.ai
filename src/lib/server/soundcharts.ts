// Soundcharts API v2 Integration
// Documentation: https://doc.api.soundcharts.com/api/v2/doc

import type { ArtistMetadata } from '$lib/types/stats';
import { SOUNDCHARTS_API_BASE, SOUNDCHARTS_API_KEY, SOUNDCHARTS_APP_ID } from '$env/static/private';
import logger from '$lib/utils/logger';

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

// Core API functions
async function fetchFromSoundcharts<T>(
  endpoint: string,
  params?: Record<string, string>
): Promise<T | null> {
  if (!SOUNDCHARTS_API_KEY || !SOUNDCHARTS_APP_ID) {
    logger.error('Missing required Soundcharts API credentials');
    return null;
  }

  const url = new URL(`${SOUNDCHARTS_API_BASE}${endpoint}`);

  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      url.searchParams.append(key, value);
    });
  }

  try {
    const response = await fetch(url.toString(), {
      headers: {
        Accept: 'application/json',
        'x-app-id': SOUNDCHARTS_APP_ID,
        'x-api-key': SOUNDCHARTS_API_KEY,
      },
    });

    if (!response.ok) {
      logger.error(`Soundcharts API request failed for URL: ${url.toString()}`);
      return null;
    }

    return response.json();
  } catch (err) {
    logger.error(`Failed to fetch from Soundcharts API URL: ${url.toString()}`, err);
    return null;
  }
}

export async function getArtistStats(artistId: string) {
  try {
    const [metadataRes, streamingRes, followersRes] = await Promise.all([
      fetchFromSoundcharts<SoundchartsResponse<ArtistMetadata>>(`/api/v2.9/artist/${artistId}`),
      fetchFromSoundcharts<SoundchartsResponse<StreamingStats>>(
        `/api/v2/artist/${artistId}/streaming`
      ),
      fetchFromSoundcharts<SoundchartsResponse<FollowersStats>>(
        `/api/v2/artist/${artistId}/followers`
      ),
    ]);

    return {
      metadata: {
        ...defaultResponses.metadata,
        object: { ...defaultResponses.metadata.object, ...(metadataRes?.data || {}) },
      },
      streaming: {
        ...defaultResponses.streaming,
        object: { ...defaultResponses.streaming.object, ...(streamingRes?.data || {}) },
      },
      followers: {
        ...defaultResponses.followers,
        object: { ...defaultResponses.followers.object, ...(followersRes?.data || {}) },
      },
    };
  } catch (err) {
    logger.error('Failed to fetch artist stats:', err);
    return defaultResponses;
  }
}

export async function getArtistIdFromSpotify(spotifyId: string): Promise<string | null> {
  try {
    const response = await fetchFromSoundcharts<SoundchartsResponse<{ id: string }>>(
      `/api/v2.9/artist/spotify/${spotifyId}`
    );
    return response?.data?.id || null;
  } catch (err) {
    logger.error('Failed to fetch artist ID from Spotify:', {
      spotifyId,
      url: `${SOUNDCHARTS_API_BASE}/api/v2.9/artist/spotify/${spotifyId}`,
      error: err,
    });
    return null;
  }
}
