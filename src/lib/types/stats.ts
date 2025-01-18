export interface StreamingMetrics {
  platform: 'spotify' | 'apple_music' | 'youtube_music' | 'soundcloud';
  streams: number;
  listeners: number;
  playlists: number;
  saves: number;
  timestamp: number;
}

export interface SocialMetrics {
  platform: 'instagram' | 'tiktok' | 'x' | 'youtube';
  followers: number;
  engagement: number;
  views: number;
  likes: number;
  comments: number;
  shares: number;
  timestamp: number;
}

export interface DashboardStats {
  followers: {
    comments: number;
    engagement: number;
    followers: number;
    likes: number;
    shares: number;
    views: number;
    platform: string;
  };
  streaming: {
    streams: number;
    listeners: number;
    playlists: number;
    shares: number;
    views: number;
    timestamp: number;
    platform: string;
  };
}
