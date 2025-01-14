import { z } from 'zod';

export const artistSchema = z.object({
  // System and required fields
  id: z.string().regex(/^[a-z0-9]+$/).length(15),
  stage_name: z.string().min(1, 'Stage name is required'),
  legal_name: z.string().min(1, 'Legal name is required'),
  email: z.string().email('Invalid email address'),
  
  // Optional text fields
  slug: z.string().nullable(),
  phone: z.string().nullable(),
  city: z.string().nullable(),
  biography: z.string().nullable(),
  
  // Date fields
  birthdate: z.string().nullable(), // Using string for HTML date input compatibility
  created: z.string().optional(), // autodate
  updated: z.string().optional(), // autodate
  
  // Relation fields
  country: z.string().nullable(), // relation field ID
  anr: z.string().nullable(), // relation field ID
  
  // File field
  artist_photos: z.array(z.string()).nullable(),
  
  // URL fields - all optional
  website: z.string().url('Invalid website URL').nullable(),
  spotify: z.string().url('Invalid Spotify URL').regex(/^https?:\/\/(?:open\.spotify\.com)/).nullable(),
  apple_music: z.string().url('Invalid Apple Music URL').regex(/^https?:\/\/(?:music\.apple\.com)/).nullable(),
  bandcamp: z.string().url('Invalid Bandcamp URL').regex(/^https?:\/\/.*?\.?bandcamp\.com/).nullable(),
  mixcloud: z.string().url('Invalid Mixcloud URL').regex(/^https?:\/\/(?:.*?\.)?mixcloud\.com/).nullable(),
  snapchat: z.string().url('Invalid Snapchat URL').regex(/^https?:\/\/(?:.*?\.)?snapchat\.com/).nullable(),
  twitch: z.string().url('Invalid Twitch URL').regex(/^https?:\/\/(?:.*?\.)?twitch\.com/).nullable(),
  youtube: z.string().url('Invalid YouTube URL').regex(/^https?:\/\/(?:.*?\.)?youtube\.com/).nullable(),
  instagram: z.string().url('Invalid Instagram URL').regex(/^https?:\/\/(?:.*?\.)?instagram\.com/).nullable(),
  facebook: z.string().url('Invalid Facebook URL').regex(/^https?:\/\/(?:.*?\.)?facebook\.com/).nullable(),
  x: z.string().url('Invalid X/Twitter URL').regex(/^https?:\/\/(?:.*?\.)?(x\.com|twitter\.com)/).nullable(),
  tiktok: z.string().url('Invalid TikTok URL').regex(/^https?:\/\/(?:.*?\.)?tiktok\.com/).nullable(),
  soundcloud: z.string().url('Invalid SoundCloud URL').regex(/^https?:\/\/(?:.*?\.)?soundcloud\.com/).nullable(),
  songkick: z.string().url('Invalid Songkick URL').regex(/^https?:\/\/(?:.*?\.)?songkick\.com/).nullable(),
  bandsintown: z.string().url('Invalid Bandsintown URL').regex(/^https?:\/\/(?:.*?\.)?bandsintown\.com/).nullable(),
  linkedin: z.string().url('Invalid LinkedIn URL').regex(/^https?:\/\/(?:.*?\.)?linkedin\.com/).nullable()
});

export type Artist = z.infer<typeof artistSchema>;