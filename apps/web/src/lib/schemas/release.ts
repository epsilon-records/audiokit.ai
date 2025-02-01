import { z } from 'zod';

export const releaseSchema = z.object({
  id: z.string().length(15).regex(/^[a-z0-9]+$/),
  org_id: z.string(),
  release_title: z.string().min(1),
  release_version: z.string().optional(),
  slug: z.string().optional(),
  release_date: z.string().optional(), // date fields come as ISO strings
  upc_code: z.string().optional(),
  catalog_number: z.string().optional(),
  description: z.string().optional(),
  cover_artwork: z.array(z.any()), // File type - we'll accept any for the form
  media_assets: z.array(z.any()).optional(), // Optional file array
  label: z.string().optional(), // Relation fields are represented by IDs
  language: z.string(), // Required relation
  genre: z.string(), // Required relation
  subgenre: z.string(), // Required relation
  is_compilation: z.boolean().optional(),
  contracts: z.array(z.any()).optional(), // Optional file array
  tracks: z.array(z.string()), // Array of track IDs
  bandcamp: z.string().url().optional(),
  vinyl: z.string().url().optional(),
  created: z.string().optional(), // autodate fields
  updated: z.string().optional(), // autodate fields
});

export type Release = z.infer<typeof releaseSchema>; 