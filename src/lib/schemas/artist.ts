import { z } from 'zod';

export const artistSchema = z.object({
    id: z.string().length(15).regex(/^[a-z0-9]+$/),
    org_id: z.string().optional(),
    test_org_id: z.string().optional(),
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
    website: z.string().url().optional().nullable(),
    spotify: z.string().url().regex(/^https?:\/\/open\.spotify\.com/).optional(),
    apple_music: z.string().url().regex(/^https?:\/\/music\.apple\.com/).optional(),
    bandcamp: z.string().url().optional(),
    mixcloud: z.string().url().regex(/^https?:\/\/mixcloud\.com/).optional(),
    snapchat: z.string().url().regex(/^https?:\/\/snapchat\.com/).optional(),
    twitch: z.string().url().regex(/^https?:\/\/twitch\.tv/).optional(),
    youtube: z.string().url().regex(/^https?:\/\/youtube\.com/).optional(),
    instagram: z.string().url().regex(/^https?:\/\/instagram\.com/).optional(),
    facebook: z.string().url().regex(/^https?:\/\/facebook\.com/).optional(),
    x: z.string().url().regex(/^https?:\/\/(x|twitter)\.com/).optional(),
    tiktok: z.string().url().regex(/^https?:\/\/tiktok\.com/).optional(),
    soundcloud: z.string().url().regex(/^https?:\/\/soundcloud\.com/).optional(),
    songkick: z.string().url().regex(/^https?:\/\/songkick\.com/).optional(),
    bandsintown: z.string().url().regex(/^https?:\/\/bandsintown\.com/).optional(),
    linkedin: z.string().url().regex(/^https?:\/\/linkedin\.com/).optional(),
    
    created: z.string().optional(),
    updated: z.string().optional()
});

export type Artist = z.infer<typeof artistSchema>;