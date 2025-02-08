/* CONFIDENTIAL AND PROPRIETARY
 * 
 * Copyright (c) 2025 AudioKit.ai. All rights reserved.
 * 
 * This software is confidential and proprietary.
 */

* 
 * This software is confidential and proprietary.
 */

export interface Artist {
  id: string;
  org_id?: string;
  stage_name?: string;
  legal_name?: string;
  is_signed?: boolean;
  email: string;
  phone?: string;
  birthdate?: string;
  artist_photos?: string[];
  city?: string;
  country?: string;
  biography?: string;
  website?: string;
  spotify?: string;
  apple_music?: string;
  bandcamp?: string;
  mixcloud?: string;
  snapchat?: string;
  twitch?: string;
  youtube?: string;
  instagram?: string;
  facebook?: string;
  x?: string;
  tiktok?: string;
  soundcloud?: string;
  songkick?: string;
  bandsintown?: string;
  linkedin?: string;
  anr?: string;
  metadata: {
    uuid: string;
    slug: string;
    name: string;
    appUrl: string;
    imageUrl: string;
    countryCode: string;
    genres: {
      root: string;
      sub: string[];
    }[];
    biography: string;
    isni: string;
    ipi: string;
    gender: 'male' | 'female' | 'other';
    type: 'person' | 'group';
    birthDate: string | null;
  };
  followers: {
    spotify: number;
    instagram: number;
    twitter: number;
    facebook: number;
  };
  streaming: {
    spotify: {
      related: {
        artist: {
          uuid: string;
          slug: string;
          name: string;
          appUrl: string;
          imageUrl: string;
        };
        platform: string;
        lastCrawlDate: string;
      };
      items: {
        date: string;
        value: number;
      }[];
      page: {
        offset: number;
        limit: number;
        next: string | null;
        previous: string | null;
        total: number;
      };
      errors: any[];
    };
  };
  tracks: Track[];
  created?: string;
  updated?: string;
}

export interface Track {
  uuid: string;
  name: string;
  creditName: string;
  releaseDate: string | null;
}
