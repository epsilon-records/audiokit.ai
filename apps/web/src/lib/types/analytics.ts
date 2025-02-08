/* CONFIDENTIAL AND PROPRIETARY
 * 
 * Copyright (c) 2025 AudioKit.ai. All rights reserved.
 * 
 * This software is confidential and proprietary.
 */

* 
 * This software is confidential and proprietary.
 */

interface StreamingMetrics {
  platform: 'spotify' | 'apple_music' | 'youtube_music' | 'soundcloud';
  streams: number;
  revenue: number;
  listeners: number;
  saves: number;
  playlists: number;
  timestamp: Date;
}

interface SocialMetrics {
  platform: 'instagram' | 'tiktok' | 'x' | 'youtube';
  followers: number;
  engagement: number;
  views: number;
  likes: number;
  comments: number;
  shares: number;
  timestamp: Date;
}

interface RevenueMetrics {
  source: 'streaming' | 'sales' | 'licensing' | 'merchandise';
  amount: number;
  currency: string;
  timestamp: Date;
}

interface AnalyticsDashboard {
  streaming: StreamingMetrics[];
  social: SocialMetrics[];
  revenue: RevenueMetrics[];
  dateRange: {
    start: Date;
    end: Date;
  };
}
