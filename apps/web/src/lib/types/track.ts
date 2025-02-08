/* CONFIDENTIAL AND PROPRIETARY
 * 
 * Copyright (c) 2025 AudioKit.ai. All rights reserved.
 * 
 * This software is confidential and proprietary.
 */

* 
 * This software is confidential and proprietary.
 */

export interface Track {
  uuid: string;
  name: string;
  isrc: {
    value: string;
    countryCode: string;
    countryName: string;
  };
  creditName: string;
  artists: {
    uuid: string;
    slug: string;
    name: string;
    appUrl: string;
    imageUrl: string;
  }[];
  releaseDate: string;
  copyright: string;
  appUrl: string;
  imageUrl: string;
  duration: number;
  explicit: boolean;
  genres: {
    root: string;
    sub: string[];
  }[];
  composers: string[];
  producers: string[];
  labels: {
    name: string;
    type: string;
  }[];
  audio: {
    acousticness: number;
    danceability: number;
    energy: number;
    instrumentalness: number;
    key: number;
    liveness: number;
    loudness: number;
    mode: number;
    speechiness: number;
    tempo: number;
    timeSignature: number;
    valence: number;
  };
  languageCode: string;
}

export interface TrackCollectionResponse {
  items: Track[];
  offset: number;
  limit: number;
  total: number;
}
