import { z } from 'zod';

export const artistSchema = z.object({
    id: z.string().length(15).regex(/^[a-z0-9]+$/),
    org_id: z.string().optional(),
    stage_name: z.string().min(1),
    legal_name: z.string().min(1),
    is_signed: z.boolean().optional(),
    email: z.string().email(),
    phone: z.string().optional(),
    birthdate: z.string().optional(), // Added for form handling
    city: z.string().optional(),
    country: z.string().optional(), // Added for form handling
    biography: z.string().optional(),
    
    // URLs with domain validation where specified
    website: z.string().url().optional().or(z.literal('')),
    spotify: z.string().url().regex(/^https?:\/\/open\.spotify\.com/).optional().or(z.literal('')),
    apple_music: z.string().url().regex(/^https?:\/\/music\.apple\.com/).optional().or(z.literal('')),
    bandcamp: z.string().url().optional().or(z.literal('')),
    mixcloud: z.string().url().regex(/^https?:\/\/mixcloud\.com/).optional().or(z.literal('')),
    snapchat: z.string().url().regex(/^https?:\/\/snapchat\.com/).optional().or(z.literal('')),
    twitch: z.string().url().regex(/^https?:\/\/twitch\.tv/).optional().or(z.literal('')),
    youtube: z.string().url().regex(/^https?:\/\/youtube\.com/).optional().or(z.literal('')),
    instagram: z.string().url().regex(/^https?:\/\/instagram\.com/).optional().or(z.literal('')),
    facebook: z.string().url().regex(/^https?:\/\/facebook\.com/).optional().or(z.literal('')),
    x: z.string().url().regex(/^https?:\/\/(x|twitter)\.com/).optional().or(z.literal('')),
    tiktok: z.string().url().regex(/^https?:\/\/tiktok\.com/).optional().or(z.literal('')),
    soundcloud: z.string().url().regex(/^https?:\/\/soundcloud\.com/).optional().or(z.literal('')),
    songkick: z.string().url().regex(/^https?:\/\/songkick\.com/).optional().or(z.literal('')),
    bandsintown: z.string().url().regex(/^https?:\/\/bandsintown\.com/).optional().or(z.literal('')),
    linkedin: z.string().url().regex(/^https?:\/\/linkedin\.com/).optional().or(z.literal('')),
    
    created: z.string().optional(),
    updated: z.string().optional()
});

export type Artist = z.infer<typeof artistSchema>;